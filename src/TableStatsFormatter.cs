namespace SportEvents;

// Один спосіб друкувати рядок результатів у всіх видах протоколу.
internal static class TableStatsFormatter
{
    internal static string Format(TableRow row)
    {
        string line = row.Name.PadRight(20);
        line += row.Wins.ToString().PadLeft(4);
        line += row.Draws.ToString().PadLeft(4);
        line += row.Losses.ToString().PadLeft(4);
        line += (row.ScoredFor + ":" + row.ScoredAgainst).PadLeft(8);
        line += row.Points.ToString().PadLeft(5);
        return line;
    }
}
