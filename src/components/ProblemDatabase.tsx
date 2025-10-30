import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { toast } from 'sonner';
import { api } from '../lib/api';
import { Trash2 } from 'lucide-react';

export default function ProblemDatabase() {
  const [problems, setProblems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProblems();
  }, []);

  const fetchProblems = async () => {
    try {
      const response = await api.get('/problems');
      const data = await response.json();
      setProblems(data);
    } catch (error: any) {
      toast.error('Failed to load problems');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (problemId: number) => {
    if (!confirm('Are you sure you want to delete this problem?')) return;
    
    try {
      await api.delete(`/problems/${problemId}`);
      toast.success('Problem deleted');
      fetchProblems();
    } catch (error: any) {
      toast.error('Failed to delete problem');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Problem Database</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {loading ? (
            <p className="text-center text-muted-foreground">Loading...</p>
          ) : problems.length === 0 ? (
            <p className="text-center text-muted-foreground">No problems yet</p>
          ) : (
            <div className="space-y-3">
              {problems.map((problem) => (
                <div key={problem.id} className="p-3 border rounded-lg space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm flex-1">{problem.problem_statement}</p>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge variant="outline">ID: {problem.id}</Badge>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8 text-destructive hover:text-destructive"
                        onClick={() => handleDelete(problem.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 flex-wrap">
                    {problem.category && (
                      <Badge variant="secondary">{problem.category}</Badge>
                    )}
                    <Badge variant="outline">
                      {problem.solution_count} solution{problem.solution_count !== 1 ? 's' : ''}
                    </Badge>
                    {problem.avg_score !== null && (
                      <Badge variant={problem.avg_score >= 70 ? 'default' : 'destructive'}>
                        Avg: {problem.avg_score}
                      </Badge>
                    )}
                  </div>
                  
                  <p className="text-xs text-muted-foreground">
                    Created: {new Date(problem.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
