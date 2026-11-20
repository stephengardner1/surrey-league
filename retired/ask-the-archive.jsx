// Retired from slarchive.org on 20 Nov 2026. Last live in commit 163d93ad6d84ae8009749615b1ec805b809c24ef (files/index.html).
// To restore: paste this component back into files/index.html and re-add its route (see retired/README.md).

const AskView=({data,setView})=>{
  const[query,setQuery]=useState('');
  const[loading,setLoading]=useState(false);
  const[answer,setAnswer]=useState('');
  const[error,setError]=useState('');
  
  const exampleQueries=[
    "Which athlete improved their average position the most from one season to the next?",
    "Who has the best win rate (wins per race)?",
    "Which club has the most athletes with race wins?",
    "What's the closest team race in the database?",
    "Who are the top 5 most consistent athletes (lowest position variance)?",
    "Which venue has produced the most first-time winners?"
  ];
  
  const buildDataSummary=()=>{
    // Create a compact summary of the data for the AI
    const athletes=data.athletes.slice(0,100).map(a=>({
      name:a.name,club:a.club,wins:a.wins,top3:a.top3,top10:a.top10,races:a.races,aScores:a.aScores
    }));
    const seasons=Object.keys(data.seasonsData).sort().reverse();
    const recentRaces=data.races.slice(0,20).map(r=>({
      season:r.season,match:r.match,venue:r.venue,date:r.date,
      top10:r.results.slice(0,10).map(x=>({pos:x.pos,name:x.name,club:x.club}))
    }));
    return{
      stats:data.stats,
      seasons,
      topAthletes:athletes,
      recentRaces,
      clubHonours:data.clubAllTime,
      achievements:data.achievements
    };
  };
  
  const askQuestion=async()=>{
    if(!query.trim())return;
    setLoading(true);
    setError('');
    setAnswer('');
    
    try{
      // Build a summary since full data is too large
      const summary=buildDataSummary();
      
      // For deeper analysis, include race-by-race athlete positions
      const athleteSeasonStats={};
      data.races.forEach(race=>{
        const season=race.season;
        race.results.forEach(r=>{
          const key=r.name;
          if(!athleteSeasonStats[key])athleteSeasonStats[key]={};
          if(!athleteSeasonStats[key][season])athleteSeasonStats[key][season]={positions:[],club:r.club};
          athleteSeasonStats[key][season].positions.push(r.pos);
        });
      });
      
      // Calculate averages per season for each athlete
      const athleteSeasonAvg={};
      Object.entries(athleteSeasonStats).forEach(([name,seasons])=>{
        athleteSeasonAvg[name]={};
        Object.entries(seasons).forEach(([season,data])=>{
          const avg=data.positions.reduce((a,b)=>a+b,0)/data.positions.length;
          athleteSeasonAvg[name][season]={avg:Math.round(avg*10)/10,races:data.positions.length,club:data.club};
        });
      });
      
      const systemPrompt=`You are a helpful assistant analyzing Surrey Cross Country League data. Answer questions about race results, athlete performance, club standings, and statistics. Be specific and cite data. Format answers clearly. When referencing athletes or clubs, be precise with names.

The database contains:
- ${data.stats.totalRaces} races from ${data.stats.seasons} seasons (2014-present with full data)
- ${data.stats.totalAthletes} athletes
- ${data.stats.totalResults} individual results

Key data structures available:
1. Athletes: name, club, wins, top3, top5, top10, top20, races, aScores (A-team finishes)
2. Races: season, match number, venue, date, full results with positions
3. Season standings: club points per match, final standings
4. Club honours: titles, 2nd places, 3rd places all-time`;

      const response=await fetch('https://surrey-league-ai.stephendgardner.workers.dev',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          model:'claude-sonnet-4-20250514',
          max_tokens:1000,
          system:systemPrompt,
          messages:[{
            role:'user',
            content:`Here is a summary of the league data:

TOP 100 ATHLETES:
${JSON.stringify(summary.topAthletes,null,1)}

CLUB HONOURS (ALL-TIME):
${JSON.stringify(summary.clubHonours,null,1)}

ACHIEVEMENTS:
${JSON.stringify(summary.achievements,null,1)}

ATHLETE SEASON AVERAGES (for improvement analysis):
${JSON.stringify(Object.fromEntries(Object.entries(athleteSeasonAvg).filter(([k,v])=>Object.keys(v).length>=2).slice(0,200)),null,1)}

RECENT RACES (top 10 finishers each):
${JSON.stringify(summary.recentRaces,null,1)}

QUESTION: ${query}`
          }]
        })
      });
      
      const result=await response.json();
      if(result.error){
        setError(result.error.message||'API error');
      }else if(result.content&&result.content[0]){
        setAnswer(result.content[0].text);
      }
    }catch(e){
      setError(e.message||'Failed to get answer');
    }finally{
      setLoading(false);
    }
  };
  
  return<div className="max-w-3xl mx-auto px-4 pt-3 md:pt-6 pb-8">
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-6 h-6 text-[#1b649e]"/>
        <h1 className="text-2xl font-bold text-gray-900">Ask the Archive</h1>
      </div>
      <p className="text-sm text-gray-500">Ask questions about Surrey League history, athlete performance, club records, and more.</p>
    </div>
    
    <div className="mb-6">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={e=>setQuery(e.target.value)}
          onKeyDown={e=>e.key==='Enter'&&!loading&&askQuestion()}
          placeholder="Ask a question about the league..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1b649e] focus:border-transparent"
        />
        <button
          onClick={askQuestion}
          disabled={loading||!query.trim()}
          className={`px-6 py-3 rounded-lg flex items-center gap-2 ${loading||!query.trim()?'bg-gray-200 text-gray-500':'bg-[#1b649e] text-white hover:bg-[#134d7a]'}`}
        >
          {loading?<span className="animate-pulse">Thinking...</span>:<><Send className="w-4 h-4"/>Ask</>}
        </button>
      </div>
    </div>
    
    {!answer&&!loading&&!error&&<div className="mb-8">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">Example questions</p>
      <div className="flex flex-wrap gap-2">
        {exampleQueries.map((q,i)=><button
          key={i}
          onClick={()=>setQuery(q)}
          className="text-sm px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
        >{q}</button>)}
      </div>
    </div>}
    
    {error&&<div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 mb-4">{error}</div>}
    
    {answer&&<div className="prose prose-sm max-w-none">
      <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
        <div className="whitespace-pre-wrap text-gray-800">{answer}</div>
      </div>
      <button onClick={()=>{setAnswer('');setQuery('');}} className="mt-4 text-sm text-[#1b649e] hover:underline">Ask another question</button>
    </div>}
  </div>;
};

