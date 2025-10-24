import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Trophy, Medal, Award } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface ComparisonResultsProps {
  result: {
    winner: string;
    solution1_score: number;
    solution2_score: number;
    comparison: any;
    overall_analysis: string;
    recommendations: any;
    cfg1_mermaid: string;
    cfg2_mermaid: string;
  };
}

export const ComparisonResults = ({ result }: ComparisonResultsProps) => {
  const getWinnerBadge = (solution: string) => {
    if (result.winner === solution) {
      return <Badge className="bg-success text-success-foreground"><Trophy className="h-3 w-3 mr-1" />Winner</Badge>;
    } else if (result.winner === 'tie') {
      return <Badge variant="secondary"><Medal className="h-3 w-3 mr-1" />Tie</Badge>;
    }
    return null;
  };

  const renderMermaid = (mermaidCode: string) => {
    return (
      <div className="mermaid-container overflow-x-auto p-4 bg-muted rounded-lg">
        <pre className="mermaid text-sm">{mermaidCode}</pre>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Winner Announcement */}
      <Card className="p-6 bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
        <div className="flex items-center justify-center gap-4 mb-4">
          <Award className="h-12 w-12 text-primary" />
          <div className="text-center">
            <h2 className="text-3xl font-bold text-card-foreground mb-2">
              {result.winner === 'tie' ? 'It\'s a Tie!' : `${result.winner.toUpperCase()} Wins!`}
            </h2>
            <p className="text-muted-foreground">
              {result.winner === 'tie' 
                ? 'Both solutions are equally good'
                : `${result.winner === 'solution1' ? 'Solution 1' : 'Solution 2'} is the better solution`
              }
            </p>
          </div>
        </div>
      </Card>

      {/* Overall Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-card-foreground">Solution 1</h3>
            {getWinnerBadge('solution1')}
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-4xl font-bold text-primary">{result.solution1_score}</span>
            <span className="text-muted-foreground">/100</span>
          </div>
          <Progress value={result.solution1_score} className="h-3" />
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-card-foreground">Solution 2</h3>
            {getWinnerBadge('solution2')}
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-4xl font-bold text-primary">{result.solution2_score}</span>
            <span className="text-muted-foreground">/100</span>
          </div>
          <Progress value={result.solution2_score} className="h-3" />
        </Card>
      </div>

      {/* Detailed Results */}
      <Card className="p-6">
        <Tabs defaultValue="overview">
          <TabsList className="grid w-full grid-cols-4 mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="cfgs">CFG Diagrams</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="recommendations">Tips</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-3 text-card-foreground">Overall Analysis</h3>
              <p className="text-muted-foreground leading-relaxed">{result.overall_analysis}</p>
            </div>
          </TabsContent>

          <TabsContent value="cfgs" className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-3 text-card-foreground">Solution 1 - Control Flow Graph</h3>
              {renderMermaid(result.cfg1_mermaid)}
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3 text-card-foreground">Solution 2 - Control Flow Graph</h3>
              {renderMermaid(result.cfg2_mermaid)}
            </div>
          </TabsContent>

          <TabsContent value="metrics" className="space-y-4">
            {Object.entries(result.comparison).map(([criterion, data]: [string, any]) => (
              <div key={criterion} className="border border-border rounded-lg p-4">
                <h4 className="font-semibold capitalize mb-3 text-card-foreground">{criterion}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-muted-foreground">Solution 1</span>
                      <Badge variant={result.winner === 'solution1' ? 'default' : 'secondary'}>
                        {data.solution1.score} pts
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{data.solution1.feedback}</p>
                    {data.solution1.time_complexity && (
                      <p className="text-xs text-muted-foreground">
                        Time: {data.solution1.time_complexity}, Space: {data.solution1.space_complexity}
                      </p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-muted-foreground">Solution 2</span>
                      <Badge variant={result.winner === 'solution2' ? 'default' : 'secondary'}>
                        {data.solution2.score} pts
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{data.solution2.feedback}</p>
                    {data.solution2.time_complexity && (
                      <p className="text-xs text-muted-foreground">
                        Time: {data.solution2.time_complexity}, Space: {data.solution2.space_complexity}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </TabsContent>

          <TabsContent value="recommendations" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-border rounded-lg p-4">
                <h4 className="font-semibold mb-3 text-card-foreground">Solution 1 Improvements</h4>
                <ul className="space-y-2">
                  {result.recommendations.solution1.map((rec: string, idx: number) => (
                    <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="border border-border rounded-lg p-4">
                <h4 className="font-semibold mb-3 text-card-foreground">Solution 2 Improvements</h4>
                <ul className="space-y-2">
                  {result.recommendations.solution2.map((rec: string, idx: number) => (
                    <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
};