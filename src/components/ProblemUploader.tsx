import { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { api } from '../lib/api';

interface ProblemUploaderProps {
  onProblemUploaded: (problemData: any) => void;
}

export default function ProblemUploader({ onProblemUploaded }: ProblemUploaderProps) {
  const [problemStatement, setProblemStatement] = useState('');
  const [loading, setLoading] = useState(false);
  const [problemData, setProblemData] = useState<any>(null);

  const handleUpload = async () => {
    if (!problemStatement.trim()) {
      toast.error('Please enter a problem statement');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/upload-problem', { problem_statement: problemStatement });
      const data = await response.json();
      setProblemData(data);
      onProblemUploaded(data);
      
      if (data.status === 'found') {
        toast.success(`Similar problem found! (${Math.round(data.similarity_score * 100)}% match)`);
      } else {
        toast.success('New problem created');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to upload problem');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Problem Statement</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          placeholder="Enter the problem statement here..."
          value={problemStatement}
          onChange={(e) => setProblemStatement(e.target.value)}
          rows={6}
          className="font-mono text-sm"
        />
        
        <Button onClick={handleUpload} disabled={loading} className="w-full">
          {loading ? 'Searching...' : 'Upload Problem'}
        </Button>

        {problemData && (
          <div className="mt-4 p-4 bg-muted rounded-lg space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant={problemData.status === 'found' ? 'default' : 'secondary'}>
                {problemData.status === 'found' ? 'Existing Problem' : 'New Problem'}
              </Badge>
              {problemData.status === 'found' && (
                <Badge variant="outline">
                  {Math.round(problemData.similarity_score * 100)}% Match
                </Badge>
              )}
            </div>
            
            <p className="text-sm text-muted-foreground">
              Problem ID: {problemData.problem_id}
            </p>
            
            {problemData.reference_solution_exists ? (
              <Badge variant="default">Reference Solution Available</Badge>
            ) : (
              <Badge variant="destructive">No Reference Solution</Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
