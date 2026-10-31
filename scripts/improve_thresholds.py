from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
p=root/'src/ResultTable.cs'

def replace(s,a,b,n=1):
    if s.count(a)!=n:raise RuntimeError(f'{a[:60]!r}: expected {n}, got {s.count(a)}')
    return s.replace(a,b)
def commit(message):
    subprocess.run(['git','add','src'],cwd=root,check=True)
    subprocess.run(['git','diff','--cached','--check'],cwd=root,check=True)
    subprocess.run(['git','commit','-m',message],cwd=root,check=True,stdout=subprocess.DEVNULL)
    sha=subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=root,text=True).strip()
    print(sha,message)

s=p.read_text()
original='''        var active = new List<Participant>();
        var dnf = new List<Participant>();
        var dq = new List<Participant>();
        foreach (var p in teams)
        {
            p.Points = p.Wins * winPoints + p.Draws - p.PenaltyPoints;
            if (p.Status == "DQ")
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
            active.Add(p);
        }'''
new='''        var buckets = CollectByStatus(teams, winPoints);
        var active = buckets.Active;
        var dnf = buckets.Withdrawn;
        var dq = buckets.Disqualified;'''
s=replace(s,original,new)
marker='''    private static bool IsHigherRanking(Participant candidate, Participant current)'''
helper='''    // Групи тільки для побудови звіту; порядок у кожній групі збережено.
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

'''
s=replace(s,marker,helper+marker)
p.write_text(s,encoding='utf-8',newline='\n')
commit('refactor(ResultTable): R01b виділено класифікацію учасників з Rank')

s=p.read_text()
old='''                if (IsHigherRanking(b, a))
                {
                    active[j] = b;
                    active[j + 1] = a;
                }'''
new='''                if (!IsHigherRanking(b, a))
                    continue;
                active[j] = b;
                active[j + 1] = a;'''
s=replace(s,old,new)
p.write_text(s,encoding='utf-8',newline='\n')
commit('refactor(ResultTable): R06b зменшено вкладеність сортування')

s=p.read_text()
old='''                if (DateTime.Today < WithdrawalRuleDate)
                {
                    // до сезону 2024/25 очки анулювались
                    if (p.Points != 0)
                        Notes.Add(p.Name + ": " + p.Points + " pts annulled");
                    p.Points = 0;
                }
                Notes.Add(p.Name + " withdrew");
                buckets.Withdrawn.Add(p);'''
new='''                AddWithdrawnParticipant(buckets, p);'''
s=replace(s,old,new)
marker='''    private static bool IsHigherRanking(Participant candidate, Participant current)'''
newmethod='''    private void AddWithdrawnParticipant(TeamBuckets buckets, Participant participant)
    {
        if (DateTime.Today < WithdrawalRuleDate)
        {
            // до сезону 2024/25 очки анулювались
            if (participant.Points != 0)
                Notes.Add(participant.Name + ": " + participant.Points + " pts annulled");
            participant.Points = 0;
        }
        Notes.Add(participant.Name + " withdrew");
        buckets.Withdrawn.Add(participant);
    }

'''
s=replace(s,marker,newmethod+marker)
p.write_text(s,encoding='utf-8',newline='\n')
commit('refactor(ResultTable): R01c ізольовано історичне правило DNF')

subprocess.run(['git','tag','-f','after-refactoring'],cwd=root,check=True)
print('New end tag after-refactoring moved to finalized refactoring commit')
