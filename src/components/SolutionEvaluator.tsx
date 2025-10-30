import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Textarea } from './ui/textarea';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Label } from './ui/label';
import { toast } from 'sonner';
import { api } from '../lib/api';
import { ImagePlus, FileCode2, X } from 'lucide-react';

interface SolutionEvaluatorProps {
  problemId: number | null;
  hasReference: boolean;
}

export default function SolutionEvaluator({ problemId, hasReference }: SolutionEvaluatorProps) {
  const [loading, setLoading] = useState(false);
  const [solutionType, setSolutionType] = useState<'flowchart' | 'pseudocode'>('pseudocode');
  const [pseudocode, setPseudocode] = useState('');
  const [flowchartImage, setFlowchartImage] = useState('');
  const [evaluation, setEvaluation] = useState<any>(null);

  useEffect(() => {
    if (evaluation?.mermaid_diagrams?.user && evaluation?.mermaid_diagrams?.reference) {
      const renderMermaid = async () => {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({ startOnLoad: false, theme: 'dark' });
        
        const elements = document.querySelectorAll('.mermaid');
        elements.forEach(el => el.removeAttribute('data-processed'));
        
        setTimeout(() => {
          mermaid.run().catch(err => console.error('Mermaid error:', err));
        }, 100);
      };
      renderMermaid();
    }
  }, [evaluation]);

  const handleEvaluate = async () => {
    if (!problemId) {
      toast.error('Please upload a problem first');
      return;
    }

    if (!hasReference) {
      toast.error('No reference solution available for this problem');
      return;
    }

    const content = solutionType === 'pseudocode' ? pseudocode : flowchartImage;
    if (!content.trim()) {
      toast.error('Please provide your solution');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/evaluate-solution', {
        problem_id: problemId,
        solution_type: solutionType,
        solution_content: content
      });
      const data = await response.json();
      
      setEvaluation(data);
      toast.success(`Evaluation complete! Score: ${data.total_score}/100`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to evaluate solution');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFlowchartImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Solution</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs value={solutionType} onValueChange={(v) => setSolutionType(v as any)}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="pseudocode" className="gap-2">
              <FileCode2 className="h-4 w-4" />
              Pseudocode
            </TabsTrigger>
            <TabsTrigger value="flowchart" className="gap-2">
              <ImagePlus className="h-4 w-4" />
              Flowchart
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="pseudocode" className="space-y-2">
            <Label>Enter Pseudocode</Label>
            <Textarea
              placeholder="Enter your pseudocode solution..."
              value={pseudocode}
              onChange={(e) => setPseudocode(e.target.value)}
              rows={10}
              className="font-mono text-sm"
            />
          </TabsContent>
          
          <TabsContent value="flowchart" className="space-y-4">
            <Label>Upload Flowchart Image</Label>
            {!flowchartImage ? (
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors">
                <input
                  type="file"
                  id="flowchart-upload"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <label htmlFor="flowchart-upload" className="cursor-pointer">
                  <ImagePlus className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Click to upload flowchart image
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    PNG, JPG, JPEG (max 5MB)
                  </p>
                </label>
              </div>
            ) : (
              <div className="relative border border-border rounded-lg p-4">
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute top-2 right-2 z-10"
                  onClick={() => setFlowchartImage('')}
                >
                  <X className="h-4 w-4" />
                </Button>
                <img src={flowchartImage} alt="Your flowchart" className="max-w-full h-auto mx-auto rounded" />
              </div>
            )}
          </TabsContent>
        </Tabs>

        <Button 
          onClick={handleEvaluate} 
          disabled={!problemId || !hasReference || loading} 
          className="w-full"
        >
          {loading ? 'Evaluating...' : 'Evaluate Solution'}
        </Button>

        {evaluation && (
          <div className="space-y-4 mt-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Evaluation Results</h3>
              <Badge variant={evaluation.total_score >= 70 ? 'default' : 'destructive'}>
                {evaluation.total_score}/100
              </Badge>
            </div>

            <div className="space-y-3">
              {Object.entries(evaluation.breakdown).map(([key, value]: [string, any]) => (
                <div key={key} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                    <span>{value.score}/{key === 'structural_similarity' ? 40 : key === 'control_flow_coverage' ? 30 : key === 'correctness' ? 20 : 10}</span>
                  </div>
                  <Progress value={(value.score / (key === 'structural_similarity' ? 40 : key === 'control_flow_coverage' ? 30 : key === 'correctness' ? 20 : 10)) * 100} />
                  <p className="text-xs text-muted-foreground">{value.feedback}</p>
                </div>
              ))}
            </div>

            {evaluation.cfg_comparison?.differences?.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm">Differences:</h4>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {evaluation.cfg_comparison.differences.map((diff: string, i: number) => (
                    <li key={i} className="text-muted-foreground">{diff}</li>
                  ))}
                </ul>
              </div>
            )}

            {evaluation.recommendations?.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm">Recommendations:</h4>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {evaluation.recommendations.map((rec: string, i: number) => (
                    <li key={i} className="text-blue-600">{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            {evaluation.mermaid_diagrams && evaluation.mermaid_diagrams.user && evaluation.mermaid_diagrams.reference && (
              <Card className="mt-6 border-2">
                <CardHeader className="bg-muted/50">
                  <CardTitle className="text-base">CFG Comparison</CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="border-blue-500/50">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-blue-600 dark:text-blue-400">Your Solution</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="p-4 bg-white dark:bg-gray-950 rounded-lg overflow-auto border">
                          <div className="mermaid">{evaluation.mermaid_diagrams.user}</div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="border-green-500/50">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-green-600 dark:text-green-400">Reference Solution</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="p-4 bg-white dark:bg-gray-950 rounded-lg overflow-auto border">
                          <div className="mermaid">{evaluation.mermaid_diagrams.reference}</div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
