from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
src=root/'src'
for name in ['ReportPrinter.cs','TournamentRepository.cs']:
 p=src/name
 s=p.read_text()
 block='''            string line = r.Name.PadRight(20);
            line += r.Wins.ToString().PadLeft(4);
            line += r.Draws.ToString().PadLeft(4);
            line += r.Losses.ToString().PadLeft(4);
            line += (r.ScoredFor + ":" + r.ScoredAgainst).PadLeft(8);
            line += r.Points.ToString().PadLeft(5);'''
 count=s.count(block)
 assert count==(2 if name=='ReportPrinter.cs' else 1),(name,count)
 call='            string line = TableStatsFormatter.Format(r);' if name=='ReportPrinter.cs' else '            string line = TableStatsFormatter.Format(RankingRowMapper.Create(r, 0, ""));'
 p.write_text(s.replace(block,call),encoding='utf-8',newline='\n')
(src/'TableStatsFormatter.cs').write_text('''namespace SportEvents;

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
''',encoding='utf-8',newline='\n')
subprocess.run(['git','add','src'],cwd=root,check=True)
subprocess.run(['git','diff','--cached','--check'],cwd=root,check=True)
subprocess.run(['git','commit','-m','refactor(ReportPrinter): R09b винесено повторений формат рядка у TableStatsFormatter'],cwd=root,check=True,stdout=subprocess.DEVNULL)
subprocess.run(['git','tag','-f','after-refactoring'],cwd=root,check=True)
