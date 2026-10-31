"""Small, reviewable transformations of the ORIGINAL donated legacy sources.

This script is a RECIPE for reproducing the committed history. Running it on an already
refactored checkout is not supported. It does not make any build/test success claims.
"""
from pathlib import Path
import subprocess,re
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src'

def read(name):return (SRC/name).read_text(encoding='utf-8')
def write(name,src):(SRC/name).write_text(src,encoding='utf-8',newline='\n')
def swap(src,old,new,n=1):
    actual=src.count(old)
    if actual != n:raise ValueError(f'Expected {n} occurrences, got {actual}; old={old[:100]!r}')
    return src.replace(old,new)
def shell(*args):
    p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout+'\n'+p.stderr)
    return p.stdout.strip()
def checkpoint(code,subject,description):
    # Basic source structural guard only; cannot replace C# compiler or actual xUnit.
    for file in SRC.glob('*.cs'):
        text=file.read_text(encoding='utf-8')
        assert text.count('{')==text.count('}'), f'Unbalanced braces in {file.name}'
    shell('git','add','src')
    shell('git','diff','--cached','--check')
    shell('git','commit','-m',f'refactor({subject}): {code} {description}')
    print(code,shell('git','rev-parse','--short','HEAD'),description)

# R02 Rename
s=read('ResultTable.cs')
s=re.sub(r'\brepo\b','_repository',s)
write('ResultTable.cs',s)
checkpoint('R02','ResultTable','перейменовано repo у _repository')

# R03 Extract Variable: decompose the candidate/current three-level sort predicate
s=read('ResultTable.cs')
old='''                if (b.Points > a.Points || (b.Points == a.Points
                    && (b.ScoredFor - b.ScoredAgainst > a.ScoredFor - a.ScoredAgainst
                    || (b.ScoredFor - b.ScoredAgainst == a.ScoredFor - a.ScoredAgainst
                    && b.Wins > a.Wins))))'''
new='''                int candidateDifference = b.ScoredFor - b.ScoredAgainst;
                int currentDifference = a.ScoredFor - a.ScoredAgainst;
                bool morePoints = b.Points > a.Points;
                bool betterDifference = b.Points == a.Points && candidateDifference > currentDifference;
                bool moreWins = b.Points == a.Points && candidateDifference == currentDifference && b.Wins > a.Wins;
                if (morePoints || betterDifference || moreWins)'''
s=swap(s,old,new)
write('ResultTable.cs',s)
checkpoint('R03','ResultTable','виділено змінні трирівневого порівняння')

# R01 Extract Method: unify the equivalent sort/order rule
s=read('ResultTable.cs')
old='''                int candidateDifference = b.ScoredFor - b.ScoredAgainst;
                int currentDifference = a.ScoredFor - a.ScoredAgainst;
                bool morePoints = b.Points > a.Points;
                bool betterDifference = b.Points == a.Points && candidateDifference > currentDifference;
                bool moreWins = b.Points == a.Points && candidateDifference == currentDifference && b.Wins > a.Wins;
                if (morePoints || betterDifference || moreWins)'''
s=swap(s,old,'                if (IsHigherRanking(b, a))')
old='''            if (i == 0 || up.Points > p.Points || (up.Points == p.Points
                && (up.ScoredFor - up.ScoredAgainst > p.ScoredFor - p.ScoredAgainst
                || (up.ScoredFor - up.ScoredAgainst == p.ScoredFor - p.ScoredAgainst
                && up.Wins > p.Wins))))'''
s=swap(s,old,'            if (i == 0 || IsHigherRanking(up, p))')
anchor='''    // старий виклик з першої версії сайту'''
method='''    private static bool IsHigherRanking(Participant candidate, Participant current)
    {
        int candidateDifference = candidate.ScoredFor - candidate.ScoredAgainst;
        int currentDifference = current.ScoredFor - current.ScoredAgainst;
        bool morePoints = candidate.Points > current.Points;
        bool betterDifference = candidate.Points == current.Points && candidateDifference > currentDifference;
        bool moreWins = candidate.Points == current.Points && candidateDifference == currentDifference
            && candidate.Wins > current.Wins;
        return morePoints || betterDifference || moreWins;
    }

'''
s=swap(s,anchor,method+anchor)
write('ResultTable.cs',s)
checkpoint('R01','ResultTable','виділено IsHigherRanking і прибрано дубль')

# R15 Replace Temp with Query
s=read('ResultTable.cs')
s=swap(s,'        int candidateDifference = candidate.ScoredFor - candidate.ScoredAgainst;\n','')
s=swap(s,'        int currentDifference = current.ScoredFor - current.ScoredAgainst;\n','')
s=swap(s,'candidateDifference > currentDifference','GoalDifference(candidate) > GoalDifference(current)')
s=swap(s,'candidateDifference == currentDifference','GoalDifference(candidate) == GoalDifference(current)')
anchor='''    private static bool IsHigherRanking(Participant candidate, Participant current)'''
s=swap(s,anchor,'''    private static int GoalDifference(Participant participant)
    {
        return participant.ScoredFor - participant.ScoredAgainst;
    }

'''+anchor)
write('ResultTable.cs',s)
checkpoint('R15','ResultTable','тимчасові різниці замінено на запит GoalDifference')

# R10 Move Method to Participant: team owns its goal difference
s=read('ResultTable.cs')
s=swap(s,'''    private static int GoalDifference(Participant participant)
    {
        return participant.ScoredFor - participant.ScoredAgainst;
    }

''','')
s=s.replace('GoalDifference(candidate)','candidate.GoalDifference()').replace('GoalDifference(current)','current.GoalDifference()')
write('ResultTable.cs',s)
s=read('Participant.cs')
anchor='''    public Participant(int id, string name, string city, string division)'''
s=swap(s,anchor,'''    public int GoalDifference()
    {
        return ScoredFor - ScoredAgainst;
    }

'''+anchor)
write('Participant.cs',s)
checkpoint('R10','Participant','обчислення різниці голів перенесено до учасника')

# R04 Replace Magic Number with Constant (legacy historical date is preserved)
s=read('ResultTable.cs')
anchor='''    public static int RankCalls = 0;'''
s=swap(s,anchor,'''    private const int StandardWinPoints = 3;
    private static readonly DateTime WithdrawalRuleDate = new DateTime(2024, 8, 1);
'''+anchor)
s=swap(s,'DateTime.Today < new DateTime(2024, 8, 1)','DateTime.Today < WithdrawalRuleDate')
s=swap(s,'return Rank(teams, 3, 0, true);','return Rank(teams, StandardWinPoints, 0, true);')
s=swap(s,'return Rank(list, 3, round, true);','return Rank(list, StandardWinPoints, round, true);')
write('ResultTable.cs',s)
checkpoint('R04','ResultTable','замінено дату і 3 очки на названі сталі')

# R06 Replace Nested Conditional with Guard Clauses on classification
s=read('ResultTable.cs')
old='''            if (p.Status == "DQ")
            {
                Console.WriteLine("  (" + p.Name + " is disqualified, no place)");
                dq.Add(p);
            }
            else if (p.Status == "DNF")
            {
                if (DateTime.Today < WithdrawalRuleDate)
                {
                    // до сезону 2024/25 очки анулювались
                    if (p.Points != 0)
                        Notes.Add(p.Name + ": " + p.Points + " pts annulled");
                    p.Points = 0;
                }
                Notes.Add(p.Name + " withdrew");
                dnf.Add(p);
            }
            else
                active.Add(p);'''
new='''            if (p.Status == "DQ")
            {
                Console.WriteLine("  (" + p.Name + " is disqualified, no place)");
                dq.Add(p);
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
                dnf.Add(p);
                continue;
            }
            active.Add(p);'''
s=swap(s,old,new)
write('ResultTable.cs',s)
checkpoint('R06','ResultTable','охоронні перевірки для DQ і DNF')

# R05 Decompose Conditional: define an intention-revealing status predicate
s=read('TournamentRepository.cs')
s=swap(s,'if (!withOut && (p.Status == "DNF" || p.Status == "DQ"))','if (!withOut && IsWithdrawnOrDisqualified(p))')
anchor='''    // Перенесення зі старої таблиці (Excel) посеред сезону.'''
s=swap(s,anchor,'''    private static bool IsWithdrawnOrDisqualified(Participant participant)
    {
        return participant.Status == "DNF" || participant.Status == "DQ";
    }

'''+anchor)
write('TournamentRepository.cs',s)
checkpoint('R05','TournamentRepository','умову виключення команд виділено у предикат')

# R09 Extract Class: move rank row mapping into RankingRowMapper
s=read('ResultTable.cs')
old='''            var row = new TableRow();
            row.Name = p.Name;
            row.Wins = p.Wins;
            row.Draws = p.Draws;
            row.Losses = p.Losses;
            row.ScoredFor = p.ScoredFor;
            row.ScoredAgainst = p.ScoredAgainst;
            row.Points = p.Points;
            row.Place = place;
            row.Label = place.ToString();
            rows.Add(row);'''
s=swap(s,old,'''            rows.Add(RankingRowMapper.Create(p, place, place.ToString()));''')
s=swap(s,'AppendOut(rows, dnf, "DNF");','RankingRowMapper.AppendUnranked(rows, dnf, "DNF");')
s=swap(s,'AppendOut(rows, dq, "DQ");','RankingRowMapper.AppendUnranked(rows, dq, "DQ");')
old='''    private void AppendOut(List<TableRow> rows, List<Participant> list, string label)
    {
        foreach (var p in list)
        {
            var row = new TableRow();
            row.Name = p.Name;
            row.Wins = p.Wins;
            row.Draws = p.Draws;
            row.Losses = p.Losses;
            row.ScoredFor = p.ScoredFor;
            row.ScoredAgainst = p.ScoredAgainst;
            row.Points = p.Points;
            row.Place = 0;
            row.Label = label;
            rows.Add(row);
        }
    }

'''
s=swap(s,old,'')
write('ResultTable.cs',s)
write('RankingRowMapper.cs', '''namespace SportEvents;

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
''')
checkpoint('R09','ResultTable','виділено клас RankingRowMapper для рядків таблиці')

# R11 Introduce Parameter Object to MatchService.Schedule without altering public wrapper
s=read('MatchService.cs')
old='''    public string Schedule(int round, int homeId, int awayId, string hall, int days, int hour)
    {
        LastError = "";'''
new='''    public string Schedule(int round, int homeId, int awayId, string hall, int days, int hour)
    {
        return Schedule(new ScheduleRequest(round, homeId, awayId, hall, days, hour));
    }

    public string Schedule(ScheduleRequest request)
    {
        LastError = "";'''
s=swap(s,old,new)
start=s.index('    public string Schedule(ScheduleRequest request)')
end=s.index('    public bool ChangeStatus',start)
oldbody=s[start:end]
for arg in ('round','homeId','awayId','hall','days','hour'):
    repl={'round':'Round','homeId':'HomeId','awayId':'AwayId','hall':'Hall','days':'Days','hour':'Hour'}[arg]
    oldbody=re.sub(r'\b'+arg+r'\b','request.'+repl,oldbody)
s=s[:start]+oldbody+s[end:]
write('MatchService.cs',s)
write('ScheduleRequest.cs','''namespace SportEvents;

// Параметри запланованого матчу передаються як одна група значень.
public sealed record ScheduleRequest(
    int Round,
    int HomeId,
    int AwayId,
    string Hall,
    int Days,
    int Hour);
''')
checkpoint('R11','MatchService','параметри Schedule згруповано у ScheduleRequest')

# R13 Encapsulate Field/Collection
s=read('ResultTable.cs')
s=swap(s,'    public static int RankCalls = 0;','    public static int RankCalls { get; private set; } = 0;')
s=swap(s,'    public List<string> Notes = new List<string>();   // для протоколу комітету','    public List<string> Notes { get; } = new List<string>();   // для протоколу комітету')
write('ResultTable.cs',s)
checkpoint('R13','ResultTable','поля лічильника та приміток інкапсульовано')

# R17 Remove Dead Code
s=read('ResultTable.cs')
old='''        //active.Sort((x, y) => x.Points != y.Points ? y.Points - x.Points
        //    : (y.ScoredFor - y.ScoredAgainst) - (x.ScoredFor - x.ScoredAgainst));
'''
s=swap(s,old,'')
write('ResultTable.cs',s)
checkpoint('R17','ResultTable','прибрано закоментований неактивний сортувальник')

shell('git','tag','after-refactoring')
print('DONE 12 distinct catalog codes; NOTE no build/test was run by this generator.')
