import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getComparisons, exportComparison } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Loader2, FileDown, Trophy, FileCode2, ImageIcon } from "lucide-react";

export const ComparisonHistory = () => {
  const [comparisons, setComparisons] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [exportingId, setExportingId] = useState<number | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchComparisons();
  }, []);

  const fetchComparisons = async () => {
    try {
      const data = await getComparisons();
      setComparisons(data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to load comparison history",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (comparisonId: number) => {
    setExportingId(comparisonId);
    try {
      const blob = await exportComparison(comparisonId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `comparison_${comparisonId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: "Export Successful",
        description: "Comparison report downloaded as PDF"
      });
    } catch (error: any) {
      toast({
        title: "Export Failed",
        description: error.message || "Failed to export comparison",
        variant: "destructive"
      });
    } finally {
      setExportingId(null);
    }
  };

  const getTypeIcon = (type: string) => {
    return type === 'flowchart' ? <ImageIcon className="h-3 w-3" /> : <FileCode2 className="h-3 w-3" />;
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-card-foreground">Comparison History</h2>
        <p className="text-sm text-muted-foreground">Your recent solution comparisons</p>
      </div>

      <ScrollArea className="h-[600px] pr-4">
        {comparisons.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No comparisons yet. Start comparing solutions!
          </div>
        ) : (
          <div className="space-y-3">
            {comparisons.map((comparison) => (
              <Card key={comparison.id} className="p-4 hover:shadow-md transition-shadow">
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium text-card-foreground line-clamp-2 flex-1">
                      {comparison.problem_statement}
                    </p>
                    {comparison.winner && comparison.winner !== 'tie' && (
                      <Badge variant="default" className="shrink-0">
                        <Trophy className="h-3 w-3 mr-1" />
                        {comparison.winner === 'solution1' ? 'S1' : 'S2'}
                      </Badge>
                    )}
                    {comparison.winner === 'tie' && (
                      <Badge variant="secondary" className="shrink-0">Tie</Badge>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      {getTypeIcon(comparison.solution1_type)}
                      <span>S1</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {getTypeIcon(comparison.solution2_type)}
                      <span>S2</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="text-center p-2 bg-muted rounded">
                      <div className="text-xs text-muted-foreground">Solution 1</div>
                      <div className="text-lg font-bold text-card-foreground">
                        {comparison.overall_scores.solution1}
                      </div>
                    </div>
                    <div className="text-center p-2 bg-muted rounded">
                      <div className="text-xs text-muted-foreground">Solution 2</div>
                      <div className="text-lg font-bold text-card-foreground">
                        {comparison.overall_scores.solution2}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-border">
                    <span className="text-xs text-muted-foreground">
                      {new Date(comparison.created_at).toLocaleDateString()}
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport(comparison.id)}
                      disabled={exportingId === comparison.id}
                    >
                      {exportingId === comparison.id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <>
                          <FileDown className="h-3 w-3 mr-1" />
                          Export
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </ScrollArea>
    </Card>
  );
};