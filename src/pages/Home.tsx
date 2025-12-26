import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { LogOut, Database, GitCompare, ArrowRight } from "lucide-react";
import { useEffect } from "react";

const Home = () => {
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
        <header className="mb-12">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="mb-2 text-4xl font-bold text-primary md:text-5xl">
                RubriX AI
              </h1>
              <p className="text-xl text-muted-foreground">
                Algorithm Analysis and Comparison Platform
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground truncate max-w-[200px]">
                {email}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
              <ThemeToggle />
            </div>
          </div>
        </header>

        <main className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mt-12">
          {/* Problem-Solution Database Card */}
          <div
            className="group relative overflow-hidden rounded-xl border border-border bg-card p-8 transition-all hover:shadow-lg hover:border-primary/50 cursor-pointer"
            onClick={() => navigate("/problems")}
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Database className="w-32 h-32" />
            </div>
            <div className="relative z-10 space-y-4">
              <div className="p-3 bg-primary/10 w-fit rounded-lg">
                <Database className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-2xl font-bold">Problem-Solution Database</h2>
              <p className="text-muted-foreground">
                Upload problems, store reference solutions, and evaluate student
                submissions against optimal Control Flow Graphs.
              </p>
              <div className="pt-4 flex items-center text-primary font-medium group-hover:translate-x-1 transition-transform">
                Go to Database <ArrowRight className="ml-2 w-4 h-4" />
              </div>
            </div>
          </div>

          {/* Solution Comparison Tool Card */}
          <div
            className="group relative overflow-hidden rounded-xl border border-border bg-card p-8 transition-all hover:shadow-lg hover:border-primary/50 cursor-pointer"
            onClick={() => navigate("/comparator")}
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <GitCompare className="w-32 h-32" />
            </div>
            <div className="relative z-10 space-y-4">
              <div className="p-3 bg-primary/10 w-fit rounded-lg">
                <GitCompare className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-2xl font-bold">Solution Comparison Tool</h2>
              <p className="text-muted-foreground">
                Compare two algorithm solutions side-by-side to analyze
                differences in logic, complexity, and implementation.
              </p>
              <div className="pt-4 flex items-center text-primary font-medium group-hover:translate-x-1 transition-transform">
                Open Comparator <ArrowRight className="ml-2 w-4 h-4" />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Home;
