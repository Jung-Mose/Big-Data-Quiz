import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# [1-1] 데이터프레임으로 불러오기
df = pd.read_csv("서울대기오염_2019.xlsx - Sheet1.csv")

# [1-2] 분석변수만 추출 및 컬럼명 변경: date, district, pm10, pm25
df = df[["날짜", "측정소명", "미세먼지", "초미세먼지"]]
df.columns = ["date", "district", "pm10", "pm25"]
df = df[~df["date"].isin(["전체", "평균"])]

# [1-3] 결측치 확인 및 제거
df = df.dropna(subset=["date", "district", "pm10", "pm25"])

# [1-4] 자료형 변환: 문자형 → 날짜형, 실수형 등
df["date"] = pd.to_datetime(df["date"])
df["pm10"] = pd.to_numeric(df["pm10"], errors="coerce")
df["pm25"] = pd.to_numeric(df["pm25"], errors="coerce")

# [2-1] month, day 파생변수 생성
# [2-2] 계절(season) 변수 생성: month 기준으로 spring/summer/autumn/winter
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
def get_season(month):
    if month in [3, 4]:
        return "spring"
    elif month in [5, 6, 7, 8]:
        return "summer"
    elif month in [9, 10]:
        return "autumn"
    else:
        return "winter"
df["season"] = df["month"].apply(get_season)


# [3-1] 최종 분석 대상 데이터 확인
print(df.head())

# [4-1] 전체 데이터 기준 PM10 평균
# 분석결과 작성
print("연간 미세먼지 평균 PM10:", df["pm10"].mean())

# [5-1] PM10 최댓값이 발생한 날짜, 구 출력
# 분석결과 작성
print("PM10 최댓값 날짜")
print(df[df["pm10"] == df["pm10"].max()][["date", "district", "pm10"]])

district_avg = df.groupby("district")["pm10"].mean().reset_index(name="avg_pm10")

# [6-1] 각 구별 pm10 평균 계산
# [6-2] 상위 5개 구만 출력 (컬럼: district, avg_pm10)
# 분석결과 작성
print("PM10 평균 상위 5개 구:")
print(district_avg.sort_values(by="avg_pm10", ascending=False).head(5))

season_avg = df.groupby("season")[["pm10", "pm25"]].mean().reset_index()

# [7-1] 계절별 평균 pm10, pm25 동시 출력
# [7-2] 평균값 기준 오름차순 정렬 (컬럼: season, avg_pm10, avg_pm25)
# 분석결과 작성
print("계절별 평균 PM10/PM25:")
print(season_avg.sort_values(by="pm10"))

# [8-1] pm10 값을 기준으로 등급 분류 (good/normal/bad/worse)
# [8-2] 전체 데이터 기준 등급별 빈도, 비율 계산 (컬럼: pm_grade, n, pct)
# 분석결과 작성
def grade_pm10(value):
    if value <= 30:
        return "good"
    elif value <= 80:
        return "normal"
    elif value <= 150:
        return "bad"
    else:
        return "worse"
df["pm_grade"] = df["pm10"].apply(grade_pm10)

grade_dist = df["pm_grade"].value_counts().reset_index()
grade_dist.columns = ["pm_grade", "n"]
grade_dist["pct"] = (grade_dist["n"] / grade_dist["n"].sum() * 100).round(2)
print("PM10 등급 분포:\n", grade_dist)

good_ratio = (
    df[df["pm_grade"] == "good"]
    .groupby("district")
    .size()
    .reset_index(name="n")
)
total_per_district = df.groupby("district").size().reset_index(name="total")
good_ratio = good_ratio.merge(total_per_district, on="district")
good_ratio["pct"] = (good_ratio["n"] / good_ratio["total"] * 100).round(2)

# [9-1] 구별 등급 분포 중 'good' 빈도와 전체 대비 비율 계산
# [9-2] 비율(pct) 기준 내림차순 정렬 후 상위 5개 구만 출력 (컬럼: district, n, pct)
# 분석결과 작성
print("좋음 등급 비율 상위 5개 구:")
print(good_ratio.sort_values(by="pct", ascending=False).head(5))

# [10-1] x축: date, y축: pm10 (선그래프)
# [10-2] 제목: 'Daily Trend of PM10 in Seoul, 2019'
# 분석결과 작성
daily_avg = df.groupby("date")["pm10"].mean().reset_index()
plt.figure(figsize=(14, 5))
sns.lineplot(data=daily_avg, x="date", y="pm10")
plt.title("Daily Trend of PM10 in Seoul, 2019")
plt.xlabel("Date")
plt.ylabel("PM10")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

season_grade = df.groupby(["season", "pm_grade"]).size().reset_index(name="n")
season_total = df.groupby("season").size().reset_index(name="total")
season_grade = season_grade.merge(season_total, on="season")
season_grade["pct"] = (season_grade["n"] / season_grade["total"] * 100).round(2)

season_order = ["spring", "summer", "autumn", "winter"]
grade_order = ["good", "normal", "bad", "worse"]
season_grade["season"] = pd.Categorical(season_grade["season"], categories=season_order, ordered=True)
season_grade["pm_grade"] = pd.Categorical(season_grade["pm_grade"], categories=grade_order, ordered=True)

# [11-1] x축: season, y축: pct, fill: pm_grade (막대그래프 - seaborn barplot)
# [11-2] 범례: good, normal, bad, worse
# [11-3] 제목: 'Seasonal Distribution of PM10 Grades in Seoul, 2019'
# 분석 결과 작성
plt.figure(figsize=(10, 6))
sns.barplot(data=season_grade, x="season", y="pct", hue="pm_grade")
plt.title("Seasonal Distribution of PM10 Grades in Seoul, 2019")
plt.ylabel("Percentage (%)")
plt.xlabel("Season")
plt.legend(title="PM10 Grade")
plt.tight_layout()
plt.show()

# [3-2] 'card_output.csv'로 저장 (GitHub에 업로드 or 구글 드라이브 공유)
df.to_csv("card_output.csv", index=False, encoding="utf-8-sig")