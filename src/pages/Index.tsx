import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { SolutionComparator } from "@/components/SolutionComparator";
import { ComparisonHistory } from "@/components/ComparisonHistory";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { LogOut, ArrowLeft } from "lucide-react";

const Index = () => {
  const { token, email, logout, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token && !isLoading) {
      navigate("/auth");
    }
  }, [token, isLoading, navigate]);

  const handleLogout = async () => {
    await logout();
    navigate("/auth");
  };

  if (isLoading) {
    return null;
  }

  if (!token) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="mb-2 text-3xl font-bold text-primary">
                Solution Comparison Tool
              </h1>
              <p className="text-muted-foreground">
                Compare two algorithm solutions
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground truncate max-w-[200px]">
                {email}
              </span>
              <Button variant="outline" size="sm" onClick={() => navigate("/")}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
              <ThemeToggle />
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mx-auto max-w-7xl">
          <div className="lg:col-span-2">
            <SolutionComparator />
          </div>

          <div className="lg:col-span-1">
            <ComparisonHistory />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
