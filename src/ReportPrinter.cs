namespace SportEvents;

// Друк для табло в залі, ширина рядка 40 символів.
public class ReportPrinter
{
    public void PrintTable(string title, List<TableRow> rows)
    {
        Console.WriteLine("--- " + title + " ---");
        Console.WriteLine("Pos Team                   W   D   L   Goals  Pts");
        foreach (TableRow r in rows)
        {
            Console.Write(r.Label.PadRight(4));
            string line = TableStatsFormatter.Format(r);
            Console.WriteLine(line);
        }
    }

    // podium for the awards ceremony, places 1-3
    public void print_podium(List<TableRow> rows)
    {
        foreach (TableRow r in rows)
        {
            if (r.Place < 1 || r.Place > 3)
                continue;
            string medal = "Bronze";
            if (r.Place == 1)
                medal = "Gold";
            else if (r.Place == 2)
                medal = "Silver";
            Console.Write(medal.PadRight(8));
            string line = TableStatsFormatter.Format(r);
            Console.WriteLine(line);
        }
    }
}
