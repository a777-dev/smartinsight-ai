from __future__ import annotations


def generate_insights(
    profile: dict[str, object],
    stress_norm: float,
    productivity_score: float,
    addiction_label: str,
    behavioral_risk_index: float,
    cluster_label: str,
) -> list[str]:
    insights: list[str] = []

    sleep = float(profile["Sleep_Hours"])
    screen = float(profile["Screen_Time"])
    social = float(profile["Social_Media_Hours"])
    notifications = float(profile["Notifications_Per_Day"])
    activity = float(profile["Physical_Activity_Score"])
    caffeine = float(profile["Caffeine_Intake"])

    if sleep < 6.0:
        insights.append(
            f"Sleep at {sleep:.1f}h is below the 6h threshold. Lifting it toward 7h could lower "
            "stress and improve focus significantly."
        )
    if screen > 8.0:
        insights.append(
            f"Screen time of {screen:.1f}h/day pushes you into burnout territory. Trimming 1.5h "
            "is the highest-leverage change you can make today."
        )
    if social > 4.0 and sleep < 7.0:
        insights.append(
            "High social media use is co-occurring with reduced sleep. This pairing strongly "
            "predicts addiction-style patterns in the cohort."
        )
    if notifications > 180.0 and activity < 3.0:
        insights.append(
            "Heavy notification load with low physical activity is the digital fatigue signature. "
            "Schedule two 20-minute walks per day to break the loop."
        )
    if caffeine > 200.0 and sleep < 6.5:
        insights.append(
            "Caffeine intake is high while sleep is short — a feedback loop that elevates stress. "
            "Move your last cup earlier in the day."
        )
    if stress_norm > 0.55:
        insights.append(
            f"Predicted stress of {stress_norm:.2f} is in the high band. The simulator can show "
            "exactly which behavior shift cuts it the fastest."
        )
    if addiction_label == "High":
        insights.append(
            "Addiction model flags HIGH severity. Compare your screen and social media inputs "
            "with the Region-Aware Analytics page for cohort baselines."
        )
    if productivity_score < 0.5:
        insights.append(
            "Productivity model predicts impaired focus. The largest drivers are sleep and "
            "screen-time exposure — both improvable within a week."
        )
    if behavioral_risk_index > 0.45 and cluster_label == "Burnout Users":
        insights.append(
            "Your archetype lands in Burnout Users with an elevated Behavioral Risk Index. "
            "Treat sleep recovery as the top intervention."
        )

    if not insights:
        insights.append(
            "Your behavioral signals are within healthy ranges. Keep sleep and activity stable "
            "as you move into busier periods."
        )

    return insights[:5]


def build_explanations(
    impacts: dict[str, dict[str, float]],
) -> dict[str, str]:
    def top_two(metric: str) -> str:
        ranked = sorted(
            impacts.items(),
            key=lambda item: abs(item[1].get(metric, 0.0)),
            reverse=True,
        )
        named = []
        for feature, values in ranked[:2]:
            delta = values.get(metric, 0.0)
            direction = "raising" if delta > 0 else "reducing"
            named.append(f"{feature.replace('_', ' ')} ({direction} by {abs(delta):.3f})")
        return " and ".join(named) if named else "limited model sensitivity"

    return {
        "stress": f"Stress is most sensitive to: {top_two('stress')}.",
        "addiction": f"Addiction severity moves most with: {top_two('addiction')}.",
        "productivity": f"Productivity outlook responds to: {top_two('productivity')}.",
    }
