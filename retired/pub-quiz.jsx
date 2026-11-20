// Retired from slarchive.org on 20 Nov 2026. Last live in commit 163d93ad6d84ae8009749615b1ec805b809c24ef (files/index.html).
// To restore: paste this component back into files/index.html and re-add its route (see retired/README.md).

const PubQuizView=({setView})=>{
  const questions=[
    {q:"Which father/son duo holds the record for best combined score?",opts:["The Ogdens (SLH)","The Sandersons (G&G)","The Clarks (H/W)","The Makkars (SLH)"],ans:0,info:"George Ogden (24th) + David Ogden (82nd) = 106 pts at Lloyd Park, 2021/22 M4"},
    {q:"Since 2014, how many times has a team escaped the relegation zone on the final day?",opts:["0","1","2","3"],ans:1,info:"Just once: Thames Hare & Hounds in 2023/24, overcoming a 15-point deficit to climb from 9th to 8th"},
    {q:"Since 2014, how many times has a team thrown away the lead on the final day?",opts:["0","1","2","3"],ans:2,info:"Twice: H/W lost a 12-point lead to Kent in 2017/18, and G&G lost a 24-point lead to H/W in 2022/23"},
    {q:"Which team recorded the worst single-match score in a 10-team season?",opts:["Ranelagh Harriers","Epsom & Ewell","Clapham Chasers","Woking AC"],ans:2,info:"Clapham Chasers scored 917 points at Beckenham Place Park in 2025/26 M2"},
    {q:"Which team recorded the best single-match score in a 9-team season?",opts:["Hercules Wimbledon","Kent AC","Herne Hill Harriers","Thames Hare & Hounds"],ans:2,info:"Herne Hill Harriers scored 99 points twice in 2011/12 – at Wimbledon Common (M1) and Ham Lands (M2)"},
    {q:"How many times have Clapham Chasers been relegated since 2014?",opts:["1 time","2 times","3 times","4 times"],ans:2,info:"Relegated in 2017/18, 2019/20, and 2023/24 – never staying up for more than 3 consecutive seasons"},
    {q:"Which brothers hold the record for best combined score?",opts:["The Holts (H/W)","The Malletts (H/W)","The Roberts (HHH)","The Cockerells (BEL)"],ans:0,info:"Bob Holt (=1st) + Dave Holt (=1st) = 3 pts at Morden Park, 1969/70 M3. They dead-heated for the win!"},
    {q:"What is the biggest points swing between two teams in a single match?",opts:["601 points","657 points","703 points","722 points"],ans:3,info:"H/W scored 153 pts while E&E scored 875 pts at Wimbledon Common, 2024/25 M1 – a 722-point gap"},
    {q:"Which clubs have won the title despite winning only one match that season?",opts:["Belgrave Harriers only","Hercules Wimbledon and Aldershot only","Three different clubs","No club has ever done this"],ans:2,info:"BOH (1996/97), H/W (1964/65), and AFD (1975/76) all won titles with just 1 match win"},
    {q:"What is the biggest race turnout in Surrey League history?",opts:["312 finishers","327 finishers","341 finishers","354 finishers"],ans:3,info:"354 finishers at Wimbledon Common, 2023/24 M3 – the largest field in league history"}
  ];
  const[current,setCurrent]=useState(0);
  const[selected,setSelected]=useState(null);
  const[score,setScore]=useState(0);
  const[showResult,setShowResult]=useState(false);
  const[finished,setFinished]=useState(false);
  
  const handleSelect=(idx)=>{
    if(showResult)return;
    setSelected(idx);
    setShowResult(true);
    if(idx===questions[current].ans)setScore(s=>s+1);
  };
  
  const nextQuestion=()=>{
    if(current<questions.length-1){
      setCurrent(c=>c+1);
      setSelected(null);
      setShowResult(false);
    }else{
      setFinished(true);
    }
  };
  
  const restart=()=>{
    setCurrent(0);
    setSelected(null);
    setScore(0);
    setShowResult(false);
    setFinished(false);
  };
  
  if(finished){
    const comparisons=[
      {min:0,max:0,name:"Clapham's 917-pt meltdown",club:"C/C",desc:"Beckenham Place Park, 2025/26 M2. The worst single-match score on record.",isTeam:true},
      {min:1,max:1,name:"Ranelagh's 907-pt disaster",club:"RAN",desc:"West Horsley Place, 2023/24 M4. A day to forget – this one will haunt you for a while.",isTeam:true},
      {min:2,max:2,name:"Dorking's 850-pt collapse",club:"DMV",desc:"Mitcham Common, 2016/17 M3. The day the wheels came off.",isTeam:true},
      {min:3,max:3,name:"Steve Gardner",club:"BEL",desc:"17 races averaging 106th. You clearly care, but that hasn't helped your performance on this terrain."},
      {min:4,max:4,name:"David Ogden",club:"SLH",desc:"42 races averaging 135th. You clearly like this league enough to put your own son through it too."},
      {min:5,max:5,name:"David Grima",club:"H/W",desc:"40 races averaging 111th. Hercules' most persistent pack runner."},
      {min:6,max:6,name:"Jeff Cunningham",club:"HHH",desc:"39 races averaging 56th. Herne Hill's modern-era ironman."},
      {min:7,max:7,name:"Chris Greenwood",club:"KEN",desc:"28 races averaging 18th. Consistent A-team scorer."},
      {min:8,max:8,name:"John Gilbert",club:"KEN",desc:"32 races averaging 7th with 2 wins. Top 10 regular."},
      {min:9,max:9,name:"Jack Millar",club:"THH",desc:"5 wins from 9 races. Elite performer."},
      {min:10,max:10,name:"Paskar Owor",club:"BEL",desc:"The modern-era GOAT. 11 wins from 37 races, averaging 5th place."}
    ];
    const comp=comparisons.find(c=>score>=c.min&&score<=c.max)||comparisons[5];
    return<div className="max-w-2xl mx-auto px-4 pt-3 md:pt-6 pb-8">
      <button onClick={()=>goBack(setView,{type:'home'})} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 mb-1 md:mb-3 -ml-2 px-2 py-1 rounded hover:bg-gray-100"><ArrowLeft className="w-4 h-4"/>Back</button>
      <div className="text-center py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Quiz Complete!</h1>
        <div className="text-6xl font-bold text-[#1b649e] mb-6">{score}/{questions.length}</div>
        <div className="bg-gray-50 rounded-xl p-6 mb-6">
          <p className="text-sm text-gray-500 uppercase tracking-wide mb-2">You are{comp.isTeam?' equivalent to':' the'}...</p>
          <div className="flex items-center justify-center gap-3 mb-3">
            <ClubShield club={comp.club} size={32}/>
            <span className="text-2xl font-bold text-gray-900">{comp.name}</span>
          </div>
          <p className="text-gray-600">{comp.desc}</p>
        </div>
        <button onClick={restart} className="px-6 py-3 bg-[#1b649e] text-white rounded-lg hover:bg-[#134d7a] font-medium">Try Again</button>
      </div>
    </div>;
  }
  
  const q=questions[current];
  return<div className="max-w-2xl mx-auto px-4 pt-3 md:pt-6 pb-8">
    <button onClick={()=>goBack(setView,{type:'home'})} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 mb-1 md:mb-3 -ml-2 px-2 py-1 rounded hover:bg-gray-100"><ArrowLeft className="w-4 h-4"/>Back</button>
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">🍺 Surrey League Pub Quiz</h1>
      <p className="text-sm text-gray-500">Question {current+1} of {questions.length} • Score: {score}/{current+(showResult?1:0)}</p>
    </div>
    <div className="bg-gray-50 rounded-xl p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">{q.q}</h2>
      <div className="space-y-3">
        {q.opts.map((opt,i)=>{
          let cls="w-full text-left px-4 py-3 rounded-lg border-2 transition-all ";
          if(!showResult){
            cls+=selected===i?"border-[#1b649e] bg-blue-50":"border-gray-200 hover:border-gray-300 bg-white";
          }else{
            if(i===q.ans)cls+="border-green-500 bg-green-50";
            else if(i===selected)cls+="border-red-500 bg-red-50";
            else cls+="border-gray-200 bg-white opacity-50";
          }
          return<button key={i} onClick={()=>handleSelect(i)} className={cls} disabled={showResult}>
            <span className="font-medium">{String.fromCharCode(65+i)}.</span> {opt}
          </button>;
        })}
      </div>
      {showResult&&<div className={`mt-4 p-4 rounded-lg ${selected===q.ans?'bg-green-100 text-green-800':'bg-amber-100 text-amber-800'}`}>
        <p className="font-medium mb-1">{selected===q.ans?'✓ Correct!':'✗ Not quite!'}</p>
        <p className="text-sm">{q.info}</p>
      </div>}
    </div>
    {showResult&&<button onClick={nextQuestion} className="w-full py-3 bg-[#1b649e] text-white rounded-lg hover:bg-[#134d7a] font-medium">
      {current<questions.length-1?'Next Question':'See Results'}
    </button>}
  </div>;
};

