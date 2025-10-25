import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Trophy, Medal, Award } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

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

const MermaidDiagram = ({ code, id }: { code: string; id: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const renderDiagram = async () => {
      if (!code) {
        setError('No diagram code provided');
        return;
      }
      
      try {
        // Clean up any existing mermaid elements
        const existingElement = document.getElementById(`${id}-${Date.now()}`);
        if (existingElement) {
          existingElement.remove();
        }

        mermaid.initialize({
          startOnLoad: false,
          theme: 'base',
          themeVariables: {
            primaryColor: '#3b82f6',
            primaryTextColor: '#ffffff',
            primaryBorderColor: '#1e40af',
            lineColor: '#6b7280',
            secondaryColor: '#f59e0b',
            tertiaryColor: '#10b981',
            background: '#1e293b',
            mainBkg: '#334155',
            secondBkg: '#475569'
          },
          securityLevel: 'loose'
        });
        
        const uniqueId = `${id}-${Date.now()}`;
        const { svg: renderedSvg } = await mermaid.render(uniqueId, code);
        setSvg(renderedSvg);
        setError('');
      } catch (err: any) {
        console.error('Mermaid rendering error for', id, ':', err);
        console.log('Failed code:', code);
        setError(err.message || 'Failed to render diagram');
        // Show the raw code as fallback
        setSvg(`<pre class="text-xs text-muted-foreground whitespace-pre-wrap p-4 bg-slate-800 rounded">${code}</pre>`);
      }
    };

    renderDiagram();
  }, [code, id]);

  if (error && !svg) {
    return (
      <div className="text-sm text-red-400 p-4">
        <p className="font-semibold mb-2">Error rendering diagram: {error}</p>
        <pre className="text-xs text-muted-foreground whitespace-pre-wrap bg-slate-800 p-4 rounded mt-2">{code}</pre>
      </div>
    );
  }

  return (
    <div 
      ref={ref} 
      className="mermaid-diagram flex justify-center"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};

export const ComparisonResults = ({ result }: ComparisonResultsProps) => {

  const getWinnerBadge = (solution: string) => {
    if (result.winner === solution) {
      return <Badge className="bg-success text-success-foreground"><Trophy className="h-3 w-3 mr-1" />Winner</Badge>;
    } else if (result.winner === 'tie') {
      return <Badge variant="secondary"><Medal className="h-3 w-3 mr-1" />Tie</Badge>;
    }
    return null;
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
              <div className="overflow-x-auto p-4 bg-muted rounded-lg">
                <MermaidDiagram code={result.cfg1_mermaid} id="cfg1" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3 text-card-foreground">Solution 2 - Control Flow Graph</h3>
              <div className="overflow-x-auto p-4 bg-muted rounded-lg">
                <MermaidDiagram code={result.cfg2_mermaid} id="cfg2" />
              </div>
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