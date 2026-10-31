namespace SportEvents;

// Одна відповідальність: перетворити стан учасника на рядок для звіту.
internal static class RankingRowMapper
{
    internal static TableRow Create(Participant participant, int place, string label)
    {
        return new TableRow
        {
            Name = participant.Name,
            Wins = participant.Wins,
            Draws = participant.Draws,
            Losses = participant.Losses,
            ScoredFor = participant.ScoredFor,
            ScoredAgainst = participant.ScoredAgainst,
            Points = participant.Points,
            Place = place,
            Label = label
        };
    }

    internal static void AppendUnranked(List<TableRow> rows, List<Participant> list, string label)
    {
        foreach (var participant in list)
        {
            rows.Add(Create(participant, 0, label));
        }
    }
}
