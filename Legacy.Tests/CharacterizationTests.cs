using SportEvents;
using Xunit;

[assembly: CollectionBehavior(DisableTestParallelization = true)]

namespace Legacy.Tests;

/// <summary>
/// Характеризаційні тести: фіксують вихідну, у тому числі недосконалу, поведінку.
/// У жодному з refactor-комітів очікування цих тестів не змінюються.
/// </summary>
public sealed class CharacterizationTests
{
    private static Participant Team(int id, string name, int wins = 0,
        int draws = 0, int forGoals = 0, int againstGoals = 0,
        string status = "OK", int penalty = 0)
    {
        return new Participant(id, name, "Kyiv", "A")
        {
            Wins = wins, Draws = draws, ScoredFor = forGoals,
            ScoredAgainst = againstGoals, Status = status, PenaltyPoints = penalty
        };
    }

    [Fact]
    public void Rank_EmptyTeams_ReturnsEmptyList()
    {
        var actual = new ResultTable().Rank(new List<Participant>(), 3, 1, true);
        Assert.Empty(actual);
    }

    [Fact]
    public void Rank_HigherPoints_RanksFirst()
    {
        var low = Team(1, "Low", draws: 1);
        var high = Team(2, "High", wins: 2);
        var actual = new ResultTable().Rank(new List<Participant> { low, high }, 3, 1, true);
        Assert.Equal(new[] { "High", "Low" }, actual.Select(x => x.Name));
        Assert.Equal(new[] { 1, 2 }, actual.Select(x => x.Place));
        Assert.Equal(6, high.Points);
    }

    [Fact]
    public void Rank_EqualPoints_GreaterGoalDifferenceWins()
    {
        var a = Team(1, "Worse", wins: 2, forGoals: 5, againstGoals: 5);
        var b = Team(2, "Better", wins: 2, forGoals: 8, againstGoals: 1);
        var actual = new ResultTable().Rank(new List<Participant> { a, b }, 3, 1, true);
        Assert.Equal(new[] { "Better", "Worse" }, actual.Select(x => x.Name));
        Assert.Equal(new[] { 1, 2 }, actual.Select(x => x.Place));
    }

    [Fact]
    public void Rank_EqualPointsAndDifference_MoreWinsRanksFirst()
    {
        var fewerWins = Team(1, "Draws", wins: 1, draws: 3, forGoals: 4, againstGoals: 4);
        var moreWins = Team(2, "Wins", wins: 2, forGoals: 9, againstGoals: 9);
        var actual = new ResultTable().Rank(new List<Participant> { fewerWins, moreWins }, 3, 1, true);
        Assert.Equal(new[] { "Wins", "Draws" }, actual.Select(x => x.Name));
        Assert.Equal(new[] { 1, 2 }, actual.Select(x => x.Place));
    }

    [Fact]
    public void Rank_CompleteTie_SharesPlaceWithoutGap()
    {
        var a = Team(1, "Zebra", wins: 2, forGoals: 5, againstGoals: 3);
        var b = Team(2, "Alpha", wins: 2, forGoals: 8, againstGoals: 6);
        var c = Team(3, "Below", wins: 1);
        var actual = new ResultTable().Rank(new List<Participant> { a, b, c }, 3, 1, true);
        Assert.Equal(new[] { "Zebra", "Alpha", "Below" }, actual.Select(x => x.Name));
        Assert.Equal(new[] { 1, 1, 2 }, actual.Select(x => x.Place));
    }

    [Fact]
    public void Rank_ZeroResults_HasZeroPointsAndFirstPlace()
    {
        var team = Team(1, "Zero");
        var actual = new ResultTable().Rank(new List<Participant> { team }, 3, 1, true);
        Assert.Single(actual);
        Assert.Equal(0, actual[0].Points);
        Assert.Equal(1, actual[0].Place);
    }

    [Fact]
    public void Rank_PenaltyGreaterThanScore_PreservesNegativePoints()
    {
        var team = Team(1, "Penalized", penalty: 4);
        var actual = new ResultTable().Rank(new List<Participant> { team }, 3, 1, true);
        Assert.Equal(-4, actual[0].Points);
    }

    [Fact]
    public void Rank_ArchiveWinRate_UsesTwoPointsPerWin()
    {
        var team = Team(1, "Archive", wins: 2, draws: 1);
        var actual = new ResultTable().Rank(new List<Participant> { team }, 2, 3, true);
        Assert.Equal(5, actual[0].Points);
    }

    [Fact]
    public void Rank_Dnf_IsAppendedWithPlaceZero()
    {
        var active = Team(1, "Playing", wins: 1);
        var withdrawn = Team(2, "Withdrawn", wins: 8, status: "DNF");
        var table = new ResultTable();
        var actual = table.Rank(new List<Participant> { withdrawn, active }, 3, 1, true);
        Assert.Equal(new[] { "Playing", "Withdrawn" }, actual.Select(x => x.Name));
        Assert.Equal(new[] { "1", "DNF" }, actual.Select(x => x.Label));
        Assert.Equal(0, actual[1].Place);
        Assert.Contains("Withdrawn withdrew", table.Notes);
    }

    [Fact]
    public void Rank_DqExcluded_StillCalculatesDqPoints()
    {
        var dq = Team(1, "DQ", wins: 3, status: "DQ");
        var actual = new ResultTable().Rank(new List<Participant> { dq }, 3, 1, false);
        Assert.Empty(actual);
        Assert.Equal(9, dq.Points);
    }

    [Fact]
    public void Rank_DqIncluded_IsLastWithNoPlace()
    {
        var dq = Team(1, "DQ", wins: 3, status: "DQ");
        var normal = Team(2, "OK", wins: 1);
        var actual = new ResultTable().Rank(new List<Participant> { dq, normal }, 3, 1, true);
        Assert.Equal(new[] { "OK", "DQ" }, actual.Select(x => x.Name));
        Assert.Equal(new[] { "1", "DQ" }, actual.Select(x => x.Label));
        Assert.Equal(0, actual[1].Place);
    }

    [Fact]
    public void Rank_NullTeams_ThrowsNullReferenceException()
    {
        Assert.Throws<NullReferenceException>(() => new ResultTable().Rank(null, 3, 1, true));
    }

    [Fact]
    public void RankDivision_NoTeams_ReturnsNull()
    {
        var result = new ResultTable(new TournamentRepository()).RankDivision("A", 2);
        Assert.Null(result);
    }

    [Fact]
    public void RankDivision_MatchInProgress_ReturnsNull()
    {
        var repo = new TournamentRepository();
        repo.Teams.Add(Team(1, "Team"));
        repo.Matches.Add(new Match { Code = "M001", Round = 2, Status = MatchStatus.InProgress });
        Assert.Null(new ResultTable(repo).RankDivision("A", 2));
    }

    [Fact]
    public void ChangeStatus_ScheduledToInProgress_ReturnsTrue()
    {
        var repo = new TournamentRepository();
        repo.Matches.Add(new Match { Code = "M001", Status = MatchStatus.Scheduled });
        Assert.True(new MatchService(repo).ChangeStatus("M001", MatchStatus.InProgress));
        Assert.Equal(MatchStatus.InProgress, repo.Matches[0].Status);
    }

    [Fact]
    public void ChangeStatus_ScheduledToFinished_ReturnsFalse()
    {
        var repo = new TournamentRepository();
        repo.Matches.Add(new Match { Code = "M002", Status = MatchStatus.Scheduled });
        Assert.False(new MatchService(repo).ChangeStatus("M002", MatchStatus.Finished));
        Assert.Equal(MatchStatus.Scheduled, repo.Matches[0].Status);
    }

    [Fact]
    public void ChangeStatus_UnknownMatch_ReturnsFalse()
    {
        Assert.False(new MatchService(new TournamentRepository()).ChangeStatus("M999", MatchStatus.Finished));
    }
}
