# Реєстр дефектів проєктування: СР №2, варіант 20

Джерело: **не змінений** код архіву V20-SportEvents.zip, тег `baseline`. Діапазони рядків — базова версія. Всі нижче наведені цитати з реальних файлів. Тяжкість 1–5; частота 1–4; пріоритет = тяжкість × частота. Вплив та оцінки часу є інженерною оцінкою, не інструментальним виміром.

|ID|Файл:рядки|Каталог дефекту|Серйозність|Частота|Пріоритет|
|---|---|---|---:|---:|---:|
|D-01|`ResultTable.cs:21–101`|Довгий метод|5|1|5|
|D-02|`ResultTable.cs:59–64`|Дублювання коду|5|2|10|
|D-03|`ResultTable.cs:60–64`|Складний умовний вираз|5|2|10|
|D-04|`MatchService.cs:17–25`|Довгий список параметрів|4|1|4|
|D-05|`EventLog.cs:12–18`|Проковтнутий виняток|4|1|4|
|D-06|`TournamentRepository.cs:56–77`|Проковтнутий виняток|5|1|5|
|D-07|`MatchService.cs:7–9`|Тимчасове поле|3|2|6|
|D-08|`MatchService.cs:89–90`|Магічне число|3|1|3|
|D-09|`Participant.cs:5–20`|Одержимість елементарними типами|4|3|12|
|D-10|`ResultTable.cs:6–9`|Відкрите змінне поле|3|2|6|
|D-11|`ResultTable.cs:70–71`|Мертвий код|2|1|2|
|D-12|`ReportPrinter.cs:12–20`|Дублювання коду|4|3|12|
|D-13|`TournamentRepository.cs:6–9`|Відкриті поля та колекції|4|3|12|
|D-14|`MatchService.cs:43–77`|Складний контроль станів|4|1|4|
|D-15|`ResultTable.cs:38–47`|Часова залежність без шва|3|1|3|

## D-01: Довгий метод
**Місце:** `ResultTable.cs:21–101`. **Тяжкість:** 5/5, **частота:** 1, **пріоритет:** 5.
**Доказ і вплив:** Rank має 55 логічних рядків та CC≈21; класифікація, сортування, місця й логування об’єднані. Категорія: читаність, тестованість.
**Гіпотеза:** Extract Method, Extract Class. **Вигода:** 5/5, **ризик зміни поведінки:** 3/5, **планова трудомісткість:** 50 хв.

```csharp
 21:     public List<TableRow> Rank(List<Participant> teams, int winPoints, int round,
 22:         bool showDisqualified)
 23:     {
 24:         RankCalls++;
 25:         Notes.Clear();
 26:         var rows = new List<TableRow>();
 27:         var active = new List<Participant>();
 28:         var dnf = new List<Participant>();
 29:         var dq = new List<Participant>();
 30:         foreach (var p in teams)
 31:         {
```

## D-02: Дублювання коду
**Місце:** `ResultTable.cs:59–64`. **Тяжкість:** 5/5, **частота:** 2, **пріоритет:** 10.
**Доказ і вплив:** Блок порівняння очок, різниці та перемог повторений для сортування й визначення місця (рядки 60–63 і 78–81). Категорія: змінюваність.
**Гіпотеза:** Extract Method. **Вигода:** 5/5, **ризик зміни поведінки:** 2/5, **планова трудомісткість:** 35 хв.

```csharp
 59:                 Participant b = active[j + 1];
 60:                 if (b.Points > a.Points || (b.Points == a.Points
 61:                     && (b.ScoredFor - b.ScoredAgainst > a.ScoredFor - a.ScoredAgainst
 62:                     || (b.ScoredFor - b.ScoredAgainst == a.ScoredFor - a.ScoredAgainst
 63:                     && b.Wins > a.Wins))))
 64:                 {
```

## D-03: Складний умовний вираз
**Місце:** `ResultTable.cs:60–64`. **Тяжкість:** 5/5, **частота:** 2, **пріоритет:** 10.
**Доказ і вплив:** Трирівневий логічний вираз із двома перевірками рівності, && та ||, профільний дефект варіанта №20. Категорія: читаність, тестованість.
**Гіпотеза:** Extract Variable. **Вигода:** 5/5, **ризик зміни поведінки:** 2/5, **планова трудомісткість:** 20 хв.

```csharp
 60:                 if (b.Points > a.Points || (b.Points == a.Points
 61:                     && (b.ScoredFor - b.ScoredAgainst > a.ScoredFor - a.ScoredAgainst
 62:                     || (b.ScoredFor - b.ScoredAgainst == a.ScoredFor - a.ScoredAgainst
 63:                     && b.Wins > a.Wins))))
 64:                 {
```

## D-04: Довгий список параметрів
**Місце:** `MatchService.cs:17–25`. **Тяжкість:** 4/5, **частота:** 1, **пріоритет:** 4.
**Доказ і вплив:** Schedule передає 6 розрізнених аргументів, близькі за змістом значення homeId/awayId легко переплутати. Категорія: змінюваність.
**Гіпотеза:** Introduce Parameter Object. **Вигода:** 4/5, **ризик зміни поведінки:** 2/5, **планова трудомісткість:** 30 хв.

```csharp
 17:     public string Schedule(int round, int homeId, int awayId, string hall, int days, int hour)
 18:     {
 19:         LastError = "";
 20:         Participant h = repo.FindTeam(homeId);
 21:         Participant a = repo.FindTeam(awayId);
 22:         if (h == null || a == null)
 23:             LastError = "Team not found";
 24:         else if (homeId == awayId || h.Division != a.Division)
 25:             LastError = "Bad pair";
```

## D-05: Проковтнутий виняток
**Місце:** `EventLog.cs:12–18`. **Тяжкість:** 4/5, **частота:** 1, **пріоритет:** 4.
**Доказ і вплив:** Порожній catch приховує помилки запису журналу. Під час суто рефакторингу поведінку змінювати не можна. Категорія: надійність.
**Гіпотеза:** Окрема задача fix з тестом. **Вигода:** 3/5, **ризик зміни поведінки:** 4/5, **планова трудомісткість:** 35 хв.

```csharp
 12:         try
 13:         {
 14:             string path = Path.Combine(Path.GetTempPath(), "sport-events-journal.log");
 15:             File.AppendAllText(path, DateTime.Now.ToString("s") + " " + kind + ": " + text + "\n");
 16:         }
 17:         catch { }   // never stop the desk because of the log
 18:     }
```

## D-06: Проковтнутий виняток
**Місце:** `TournamentRepository.cs:56–77`. **Тяжкість:** 5/5, **частота:** 1, **пріоритет:** 5.
**Доказ і вплив:** ImportTeams мовчки пропускає невалідні рядки і може залишити частково додану команду в Teams. Категорія: надійність.
**Гіпотеза:** Окрема задача fix, транзакційний парсинг. **Вигода:** 3/5, **ризик зміни поведінки:** 4/5, **планова трудомісткість:** 50 хв.

```csharp
 56:                 continue;
 57:             try
 58:             {
 59:                 string[] f = ln.Split(';');
 60:                 string div = f[2].Trim().ToUpper();
 61:                 if (div != "A" && div != "B")
 62:                     div = "B";   // тимчасово: в Excel ще є стара ліга "C"
 63:                 Participant p = new Participant(Teams.Count + 1, f[0].Trim(), f[1].Trim(), div);
 64:                 Teams.Add(p);
 65:                 p.Wins = int.Parse(f[3]);
 66:                 p.Draws = int.Parse(f[4]);
```

## D-07: Тимчасове поле
**Місце:** `MatchService.cs:7–9`. **Тяжкість:** 3/5, **частота:** 2, **пріоритет:** 6.
**Доказ і вплив:** Публічне LastError — змінний стан помилки останньої операції; наступний виклик перезаписує значення. Категорія: тестованість, надійність.
**Гіпотеза:** Introduce Result або власний тип помилки. **Вигода:** 4/5, **ризик зміни поведінки:** 3/5, **планова трудомісткість:** 35 хв.

```csharp
  7:     public string LastError = "";
  8:     public int ResultsEntered = 0;
  9:     private TournamentRepository repo;
```

## D-08: Магічне число
**Місце:** `MatchService.cs:89–90`. **Тяжкість:** 3/5, **частота:** 1, **пріоритет:** 3.
**Доказ і вплив:** Число 30 у перевірці рахунку не назване правилом турніру. Категорія: читаність.
**Гіпотеза:** Replace Magic Number with Constant. **Вигода:** 4/5, **ризик зміни поведінки:** 1/5, **планова трудомісткість:** 10 хв.

```csharp
 89:         else if (home < 0 || away < 0 || home + away > 30)   // typo in the sheet
 90:             LastError = "Bad score " + home + ":" + away;
```

## D-09: Одержимість елементарними типами
**Місце:** `Participant.cs:5–20`. **Тяжкість:** 4/5, **частота:** 3, **пріоритет:** 12.
**Доказ і вплив:** Статус команди записано довільним рядком (OK/DNF/DQ), без окремого доменного типу. Категорія: змінюваність, надійність.
**Гіпотеза:** Replace Primitive with Value Object. **Вигода:** 5/5, **ризик зміни поведінки:** 4/5, **планова трудомісткість:** 55 хв.

```csharp
  5: public class Participant
  6: {
  7:     public int Id;
  8:     public string Name;
  9:     public string City;
 10:     public string Division;          // "A" - вища ліга, "B" - перша
 11:     public string Status = "OK";
 12:     public int Wins;
 13:     public int Draws;
 14:     public int Losses;
 15:     public int ScoredFor;
```

## D-10: Відкрите змінне поле
**Місце:** `ResultTable.cs:6–9`. **Тяжкість:** 3/5, **частота:** 2, **пріоритет:** 6.
**Доказ і вплив:** RankCalls і Notes були публічними змінними полями — клієнт міг скинути лічильник або замінити колекцію. Категорія: надійність.
**Гіпотеза:** Encapsulate Field / Collection. **Вигода:** 4/5, **ризик зміни поведінки:** 1/5, **планова трудомісткість:** 15 хв.

```csharp
  6: {
  7:     public static int RankCalls = 0;
  8:     public List<string> Notes = new List<string>();   // для протоколу комітету
  9:     private TournamentRepository repo;
```

## D-11: Мертвий код
**Місце:** `ResultTable.cs:70–71`. **Тяжкість:** 2/5, **частота:** 1, **пріоритет:** 2.
**Доказ і вплив:** Закоментований active.Sort — старий невикористаний алгоритм, створює шум. Категорія: читаність.
**Гіпотеза:** Remove Dead Code. **Вигода:** 3/5, **ризик зміни поведінки:** 1/5, **планова трудомісткість:** 10 хв.

```csharp
 70:         //active.Sort((x, y) => x.Points != y.Points ? y.Points - x.Points
 71:         //    : (y.ScoredFor - y.ScoredAgainst) - (x.ScoredFor - x.ScoredAgainst));
```

## D-12: Дублювання коду
**Місце:** `ReportPrinter.cs:12–20`. **Тяжкість:** 4/5, **частота:** 3, **пріоритет:** 12.
**Доказ і вплив:** Форматування таблиці з шести рядків повторено у PrintTable, print_podium та PrintDivision. Категорія: змінюваність.
**Гіпотеза:** Extract Class / Extract Method. **Вигода:** 4/5, **ризик зміни поведінки:** 2/5, **планова трудомісткість:** 30 хв.

```csharp
 12:             Console.Write(r.Label.PadRight(4));
 13:             string line = r.Name.PadRight(20);
 14:             line += r.Wins.ToString().PadLeft(4);
 15:             line += r.Draws.ToString().PadLeft(4);
 16:             line += r.Losses.ToString().PadLeft(4);
 17:             line += (r.ScoredFor + ":" + r.ScoredAgainst).PadLeft(8);
 18:             line += r.Points.ToString().PadLeft(5);
 19:             Console.WriteLine(line);
 20:         }
```

## D-13: Відкриті поля та колекції
**Місце:** `TournamentRepository.cs:6–9`. **Тяжкість:** 4/5, **частота:** 3, **пріоритет:** 12.
**Доказ і вплив:** Teams, Matches і nextMatchNo доступні для довільної заміни/модифікації ззовні. Категорія: надійність.
**Гіпотеза:** Encapsulate Field / Collection. **Вигода:** 4/5, **ризик зміни поведінки:** 4/5, **планова трудомісткість:** 60 хв.

```csharp
  6:     public static int nextMatchNo = 1;
  7:     public List<Participant> Teams = new List<Participant>();
  8:     public List<Match> Matches = new List<Match>();
  9: 
```

## D-14: Складний контроль станів
**Місце:** `MatchService.cs:43–77`. **Тяжкість:** 4/5, **частота:** 1, **пріоритет:** 4.
**Доказ і вплив:** ChangeStatus використовує switch і складну перевірку переходів стану (CC≈11). Категорія: тестованість, змінюваність.
**Гіпотеза:** Replace Conditional with Table. **Вигода:** 4/5, **ризик зміни поведінки:** 3/5, **планова трудомісткість:** 55 хв.

```csharp
 43:     public bool ChangeStatus(string code, MatchStatus newStatus)
 44:     {
 45:         Match m = repo.FindMatch(code);
 46:         if (m == null)
 47:         {
 48:             Console.WriteLine("  Match " + code + " not found");
 49:             return false;
 50:         }
 51:         bool ok = false;
 52:         switch (m.Status)
 53:         {
```

## D-15: Часова залежність без шва
**Місце:** `ResultTable.cs:38–47`. **Тяжкість:** 3/5, **частота:** 1, **пріоритет:** 3.
**Доказ і вплив:** Ветвь історичного анулювання DNF залежить від DateTime.Today і не має ін’єкції годинника. Категорія: тестованість.
**Гіпотеза:** Introduce Clock seam. **Вигода:** 3/5, **ризик зміни поведінки:** 4/5, **планова трудомісткість:** 45 хв.

```csharp
 38:             else if (p.Status == "DNF")
 39:             {
 40:                 if (DateTime.Today < new DateTime(2024, 8, 1))
 41:                 {
 42:                     // до сезону 2024/25 очки анулювались
 43:                     if (p.Points != 0)
 44:                         Notes.Add(p.Name + ": " + p.Points + " pts annulled");
 45:                     p.Points = 0;
 46:                 }
 47:                 Notes.Add(p.Name + " withdrew");
```
