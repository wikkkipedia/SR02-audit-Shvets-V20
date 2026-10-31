namespace SportEvents;

// Параметри запланованого матчу передаються як одна група значень.
public sealed record ScheduleRequest(
    int Round,
    int HomeId,
    int AwayId,
    string Hall,
    int Days,
    int Hour);
