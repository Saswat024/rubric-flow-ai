import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { History, FileCode2, Workflow } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Evaluation {
  id: number;
  type: string;
  content: string;
  result: {
    total_score: number;
    breakdown: Array<{
      criterion: string;
      score: number;
      max_score: number;
    }>;
  };
  total_score: number;
  created_at: string;
}

export const EvaluationHistory = () => {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchEvaluations();
  }, []);

  const fetchEvaluations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/evaluations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch evaluations');

      const data = await response.json();
      setEvaluations(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load evaluation history",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-green-500/10 text-green-700 dark:text-green-400";
    if (score >= 60) return "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400";
    return "bg-red-500/10 text-red-700 dark:text-red-400";
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <History className="h-5 w-5" />
          <h2 className="text-xl font-semibold">Loading history...</h2>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-4">
        <History className="h-5 w-5" />
        <h2 className="text-xl font-semibold">Evaluation History</h2>
      </div>

      {evaluations.length === 0 ? (
        <p className="text-muted-foreground text-center py-8">
          No evaluations yet. Start by evaluating a flowchart or pseudocode!
        </p>
      ) : (
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-3">
            {evaluations.map((evaluation) => (
              <div
                key={evaluation.id}
                className="flex items-start gap-3 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="mt-1">
                  {evaluation.type === 'flowchart' ? (
                    <Workflow className="h-5 w-5 text-primary" />
                  ) : (
                    <FileCode2 className="h-5 w-5 text-primary" />
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline" className="capitalize">
                      {evaluation.type}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(evaluation.created_at)}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Badge className={getScoreColor(evaluation.total_score)}>
                      Score: {evaluation.total_score}/100
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      )}
    </Card>
  );
};
