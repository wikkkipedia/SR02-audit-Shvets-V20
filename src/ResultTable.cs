namespace SportEvents;

// Турнірна таблиця: очки, різниця м'ячів, перемоги.
// Повна рівність - спільне місце, за алфавітом (п. 7.3).
public class ResultTable
{
    private const int StandardWinPoints = 3;
    private static readonly DateTime WithdrawalRuleDate = new DateTime(2024, 8, 1);
    public static int RankCalls { get; private set; } = 0;
    public List<string> Notes { get; } = new List<string>();   // для протоколу комітету
    private TournamentRepository _repository;

    public ResultTable() : this(new TournamentRepository()) { }

    public ResultTable(TournamentRepository repository)
    {
        _repository = repository;
    }

    // winPoints: 3 з сезону 2019/20, архівні таблиці - по 2.
    // DNF - після всіх без місця; DQ - в самому низу.
    // TODO: п. 7.3 - особисті зустрічі замість перемог
    public List<TableRow> Rank(List<Participant> teams, int winPoints, int round,
        bool showDisqualified)
    {
        RankCalls++;
        Notes.Clear();
        var rows = new List<TableRow>();
        var buckets = CollectByStatus(teams, winPoints);
        var active = buckets.Active;
        var dnf = buckets.Withdrawn;
        var dq = buckets.Disqualified;
        // бульбашка: List.Sort міняв місцями рівні команди
        for (int i = 0; i < active.Count - 1; i++)
        {
            for (int j = 0; j < active.Count - 1 - i; j++)
            {
                Participant a = active[j];
                Participant b = active[j + 1];
                if (IsHigherRanking(b, a))
                {
                    active[j] = b;
                    active[j + 1] = a;
                }
            }
        }
        int place = 0;
        for (int i = 0; i < active.Count; i++)
        {
            Participant p = active[i];
            Participant up = active[Math.Max(0, i - 1)];
            // нове місце, якщо команда вище строго краща
            if (i == 0 || IsHigherRanking(up, p))
            {
                place++;
            }
            rows.Add(RankingRowMapper.Create(p, place, place.ToString()));
        }
        RankingRowMapper.AppendUnranked(rows, dnf, "DNF");
        if (showDisqualified)
            RankingRowMapper.AppendUnranked(rows, dq, "DQ");
        EventLog.Write("table", "round " + round + ": " + rows.Count + " rows");
        return rows;
    }

    // Групи тільки для побудови звіту; порядок у кожній групі збережено.
    private sealed class TeamBuckets
    {
        public List<Participant> Active { get; } = new List<Participant>();
        public List<Participant> Withdrawn { get; } = new List<Participant>();
        public List<Participant> Disqualified { get; } = new List<Participant>();
    }

    private TeamBuckets CollectByStatus(List<Participant> teams, int winPoints)
    {
        var buckets = new TeamBuckets();
        foreach (var p in teams)
        {
            p.Points = p.Wins * winPoints + p.Draws - p.PenaltyPoints;
            if (p.Status == "DQ")
            {
                Console.WriteLine("  (" + p.Name + " is disqualified, no place)");
                buckets.Disqualified.Add(p);
                continue;
            }
            if (p.Status == "DNF")
            {
                if (DateTime.Today < WithdrawalRuleDate)
                {
                    // до сезону 2024/25 очки анулювались
                    if (p.Points != 0)
                        Notes.Add(p.Name + ": " + p.Points + " pts annulled");
                    p.Points = 0;
                }
                Notes.Add(p.Name + " withdrew");
                buckets.Withdrawn.Add(p);
                continue;
            }
            buckets.Active.Add(p);
        }
        return buckets;
    }

    private static bool IsHigherRanking(Participant candidate, Participant current)
    {
        bool morePoints = candidate.Points > current.Points;
        bool betterDifference = candidate.Points == current.Points && candidate.GoalDifference() > current.GoalDifference();
        bool moreWins = candidate.Points == current.Points && candidate.GoalDifference() == current.GoalDifference()
            && candidate.Wins > current.Wins;
        return morePoints || betterDifference || moreWins;
    }

    // старий виклик з першої версії сайту
    public List<TableRow> Rank(List<Participant> teams)
    {
        return Rank(teams, StandardWinPoints, 0, true);
    }

    // для сайту: поки матч туру ще йде, таблицю не даємо
    public List<TableRow> RankDivision(string division, int round)
    {
        foreach (Match m in _repository.Matches)
            if (m.Round == round && m.Status == MatchStatus.InProgress)
                return null;
        List<Participant> list = _repository.ByDivision(division, true);
        if (list.Count == 0)
        {
            Console.WriteLine("No teams in division " + division);
            return null;
        }
        return Rank(list, StandardWinPoints, round, true);
    }
}

// Рядок таблиці для друку.
public class TableRow
{
    public int Place;
    public string Label;             // місце числом або "DNF" / "DQ"
    public string Name;
    public int Wins, Draws, Losses;
    public int ScoredFor, ScoredAgainst;
    public int Points;
}
