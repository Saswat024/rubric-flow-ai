import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { SolutionInput } from "./SolutionInput";
import { ComparisonResults } from "./ComparisonResults";
import { compareSolutions } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Loader2, GitCompare } from "lucide-react";

export const SolutionComparator = () => {
  const [problemStatement, setProblemStatement] = useState("");
  const [solution1, setSolution1] = useState<{ type: 'flowchart' | 'pseudocode', content: string } | null>(null);
  const [solution2, setSolution2] = useState<{ type: 'flowchart' | 'pseudocode', content: string } | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const { toast } = useToast();

  const handleCompare = async () => {
    if (!problemStatement.trim()) {
      toast({
        title: "Missing Problem Statement",
        description: "Please enter a problem statement",
        variant: "destructive"
      });
      return;
    }

    if (!solution1 || !solution1.content) {
      toast({
        title: "Missing Solution 1",
        description: "Please provide the first solution",
        variant: "destructive"
      });
      return;
    }

    if (!solution2 || !solution2.content) {
      toast({
        title: "Missing Solution 2",
        description: "Please provide the second solution",
        variant: "destructive"
      });
      return;
    }

    setIsComparing(true);
    setComparisonResult(null);

    try {
      const result = await compareSolutions(problemStatement, solution1, solution2);
      setComparisonResult(result);
      toast({
        title: "Comparison Complete!",
        description: `Winner: ${result.winner === 'tie' ? 'It\'s a tie!' : result.winner.toUpperCase()}`
      });
    } catch (error: any) {
      toast({
        title: "Comparison Failed",
        description: error.message || "An error occurred during comparison",
        variant: "destructive"
      });
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Problem Statement */}
      <Card className="p-6">
        <h2 className="text-2xl font-semibold mb-4 text-card-foreground">Problem Statement</h2>
        <div className="space-y-2">
          <Label htmlFor="problem">Describe the problem you want to solve</Label>
          <Textarea
            id="problem"
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            placeholder="Example: Find the maximum element in an array of integers"
            className="min-h-[120px]"
          />
        </div>
      </Card>

      {/* Solutions Input */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SolutionInput 
          label="Solution 1" 
          onSolutionChange={setSolution1}
          solution={solution1}
        />
        <SolutionInput 
          label="Solution 2" 
          onSolutionChange={setSolution2}
          solution={solution2}
        />
      </div>

      {/* Compare Button */}
      <div className="flex justify-center">
        <Button
          size="lg"
          onClick={handleCompare}
          disabled={isComparing}
          className="px-8"
        >
          {isComparing ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Comparing Solutions...
            </>
          ) : (
            <>
              <GitCompare className="mr-2 h-5 w-5" />
              Compare Solutions
            </>
          )}
        </Button>
      </div>

      {/* Loading State */}
      {isComparing && (
        <Card className="p-8">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <span className="text-muted-foreground">Analyzing problem statement...</span>
            </div>
            <div className="flex items-center gap-3">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <span className="text-muted-foreground">Generating Control Flow Graphs...</span>
            </div>
            <div className="flex items-center gap-3">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <span className="text-muted-foreground">Comparing solutions...</span>
            </div>
          </div>
        </Card>
      )}

      {/* Results */}
      {comparisonResult && !isComparing && (
        <ComparisonResults result={comparisonResult} />
      )}
    </div>
  );
};