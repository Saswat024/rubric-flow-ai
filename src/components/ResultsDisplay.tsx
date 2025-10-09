import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, AlertCircle, Lightbulb } from "lucide-react";
import { EvaluationResult } from "./FlowchartEvaluator";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

interface ResultsDisplayProps {
  result: EvaluationResult;
  type: "flowchart" | "pseudocode";
}

export const ResultsDisplay = ({ result, type }: ResultsDisplayProps) => {
  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return "text-success";
    if (percentage >= 60) return "text-warning";
    return "text-destructive";
  };

  const scorePercentage = result.total_score;

  const chartData = result.breakdown.map((item) => ({
    name: item.criterion,
    score: item.score,
    maxScore: item.max_score,
    percentage: (item.score / item.max_score) * 100,
  }));

  const getFeedbackIcon = (feedback: string) => {
    if (feedback.startsWith("✅")) return <CheckCircle2 className="h-5 w-5 text-success" />;
    if (feedback.startsWith("⚠️")) return <AlertCircle className="h-5 w-5 text-warning" />;
    return <Lightbulb className="h-5 w-5 text-primary" />;
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Overall Score */}
      <Card className="p-6 bg-gradient-to-br from-card to-primary/5">
        <h2 className="mb-4 text-2xl font-semibold text-card-foreground">Overall Score</h2>
        <div className="flex items-center gap-4">
          <div className={`text-6xl font-bold ${getScoreColor(scorePercentage)}`}>
            {result.total_score}
          </div>
          <div className="flex-1">
            <div className="mb-2 text-sm text-muted-foreground">out of 100</div>
            <Progress value={scorePercentage} className="h-3" />
          </div>
        </div>
      </Card>

      {/* Rubric Breakdown */}
      <Card className="p-6">
        <h2 className="mb-4 text-2xl font-semibold text-card-foreground">Rubric Breakdown</h2>
        <div className="space-y-4 mb-6">
          {result.breakdown.map((item, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-card-foreground">{item.criterion}</span>
                <span className="text-sm text-muted-foreground">
                  {item.score}/{item.max_score} pts
                </span>
              </div>
              <Progress value={(item.score / item.max_score) * 100} className="h-2" />
              <p className="text-sm text-muted-foreground">{item.feedback}</p>
            </div>
          ))}
        </div>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis
                dataKey="name"
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
              />
              <YAxis tick={{ fill: "hsl(var(--muted-foreground))" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Legend />
              <Bar dataKey="score" fill="hsl(var(--primary))" name="Score" />
              <Bar dataKey="maxScore" fill="hsl(var(--muted))" name="Max Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Feedback Section */}
      <Card className="p-6">
        <h2 className="mb-4 text-2xl font-semibold text-card-foreground">Detailed Feedback</h2>
        <div className="space-y-3">
          {result.feedback.map((item, index) => (
            <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
              {getFeedbackIcon(item)}
              <p className="flex-1 text-sm text-card-foreground">{item}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
