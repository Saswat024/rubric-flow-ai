import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { api } from '../lib/api';

interface ReferenceSelectorProps {
  problemId: number | null;
  onReferenceLoaded: (referenceData: any) => void;
}

export default function ReferenceSelector({ problemId, onReferenceLoaded }: ReferenceSelectorProps) {
  const [loading, setLoading] = useState(false);
  const [referenceData, setReferenceData] = useState<any>(null);
  const [showUploadForm, setShowUploadForm] = useState(false);

  useEffect(() => {
    if (referenceData?.mermaid_diagram) {
      const renderMermaid = async () => {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({ startOnLoad: false, theme: 'default' });
        
        setTimeout(() => {
          mermaid.run().catch(err => console.error('Mermaid error:', err));
        }, 100);
      };
      renderMermaid();
    }
  }, [referenceData]);

  useEffect(() => {
    if (problemId) {
      setReferenceData(null);
      setShowUploadForm(false);
    }
  }, [problemId]);
  const [uploadMode, setUploadMode] = useState<'flowchart' | 'pseudocode'>('pseudocode');
  const [pseudocode, setPseudocode] = useState('');
  const [flowchartImage, setFlowchartImage] = useState('');

  const handleAutoFetch = async () => {
    if (!problemId) {
      toast.error('Please upload a problem first');
      return;
    }

    setLoading(true);
    try {
      const response = await api.get(`/fetch-reference-solution/${problemId}`);
      const data = await response.json();
      
      if (data.exists) {
        setReferenceData(data);
        onReferenceLoaded(data);
        toast.success('Reference solution loaded');
        setShowUploadForm(false);
      } else {
        toast.info('No reference solution available. Please upload one.');
        setShowUploadForm(true);
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to fetch reference');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadReference = async () => {
    if (!problemId) {
      toast.error('Please upload a problem first');
      return;
    }

    const content = uploadMode === 'pseudocode' ? pseudocode : flowchartImage;
    if (!content.trim()) {
      toast.error('Please provide solution content');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/upload-reference-solution', {
        problem_id: problemId,
        solution_type: uploadMode,
        solution_content: content
      });
      const data = await response.json();
      
      setReferenceData(data);
      onReferenceLoaded(data);
      toast.success('Reference solution uploaded successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to upload reference');
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
        <CardTitle>Reference Solution</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Button onClick={handleAutoFetch} disabled={!problemId || loading} variant="outline" className="flex-1">
            {loading ? 'Loading...' : 'Auto Fetch'}
          </Button>
          <Button onClick={() => setShowUploadForm(true)} disabled={!problemId || loading || referenceData} variant="default" className="flex-1">
            Upload
          </Button>
        </div>

        {!referenceData && showUploadForm && (
          <div className="space-y-4">
            <Tabs value={uploadMode} onValueChange={(v) => setUploadMode(v as any)}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="pseudocode">Pseudocode</TabsTrigger>
                <TabsTrigger value="flowchart">Flowchart</TabsTrigger>
              </TabsList>
              
              <TabsContent value="pseudocode" className="space-y-2">
                <Textarea
                  placeholder="Enter reference pseudocode..."
                  value={pseudocode}
                  onChange={(e) => setPseudocode(e.target.value)}
                  rows={8}
                  className="font-mono text-sm"
                />
              </TabsContent>
              
              <TabsContent value="flowchart" className="space-y-2">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="w-full"
                />
                {flowchartImage && (
                  <img src={flowchartImage} alt="Flowchart" className="max-h-64 mx-auto" />
                )}
              </TabsContent>
            </Tabs>

            <Button onClick={handleUploadReference} disabled={!problemId || loading} className="w-full">
              {loading ? 'Uploading...' : 'Upload Reference'}
            </Button>
          </div>
        )}

        {referenceData && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <Badge variant="default">Reference Available</Badge>
              <Badge variant="outline">{referenceData.solution_type}</Badge>
            </div>
            
            {referenceData.optimal_complexity && (
              <div className="text-sm space-y-1">
                <p><strong>Time:</strong> {referenceData.optimal_complexity.time}</p>
                <p><strong>Space:</strong> {referenceData.optimal_complexity.space}</p>
              </div>
            )}

            {referenceData.mermaid_diagram && (
              <div className="p-4 bg-card rounded-lg overflow-auto border">
                <div className="mermaid">{referenceData.mermaid_diagram}</div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
