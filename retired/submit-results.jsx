// Retired from slarchive.org on 20 Nov 2026. Last live in commit 163d93ad6d84ae8009749615b1ec805b809c24ef (files/index.html).
// To restore: paste this component back into files/index.html and re-add its route (see retired/README.md).

const SubmitView=({setView})=>{
  const[submitType,setSubmitType]=useState('url');
  const[url,setUrl]=useState('');
  const[file,setFile]=useState(null);
  const[notes,setNotes]=useState('');
  const[status,setStatus]=useState(null);
  const[submitting,setSubmitting]=useState(false);
  
  const handleSubmit=async(e)=>{
    e.preventDefault();
    setSubmitting(true);
    
    const formData=new FormData();
    formData.append('access_key','7f1557bd-f355-4008-a904-d892da5489b0'); // You'll replace this
    formData.append('subject','Surrey League Archive - Results Submission');
    formData.append('type',submitType);
    if(submitType==='url')formData.append('url',url);
    if(submitType==='file'&&file)formData.append('attachment',file);
    formData.append('notes',notes);
    
    try{
      const res=await fetch('https://api.web3forms.com/submit',{method:'POST',body:formData});
      if(res.ok){setStatus('success');}else{setStatus('error');}
    }catch(err){setStatus('error');}
    setSubmitting(false);
  };
  
  if(status==='success')return<div className="max-w-xl mx-auto px-4 pt-3 md:pt-6 pb-8">
    <button onClick={()=>goBack(setView,{type:'home'})} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 mb-1 md:mb-3 -ml-2 px-2 py-1 rounded hover:bg-gray-100"><ArrowLeft className="w-4 h-4"/>Back</button>
    <div className="text-center py-12">
      <div className="text-5xl mb-4">✅</div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Thanks!</h1>
      <p className="text-gray-600">Your submission has been received. We'll review it and update the archive.</p>
    </div>
  </div>;
  
  return<div className="max-w-xl mx-auto px-4 pt-3 md:pt-6 pb-8">
    <button onClick={()=>goBack(setView,{type:'home'})} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 mb-1 md:mb-3 -ml-2 px-2 py-1 rounded hover:bg-gray-100"><ArrowLeft className="w-4 h-4"/>Back</button>
    <h1 className="text-2xl font-bold text-gray-900 mb-2">Submit Results</h1>
    <p className="text-sm text-gray-500 mb-6">Help us fill in the gaps! Submit a link to results or upload a file (PDF, image, etc).</p>
    
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex gap-4">
        <label className={`flex-1 p-4 border-2 rounded-lg cursor-pointer text-center transition-all ${submitType==='url'?'border-[#1b649e] bg-blue-50':'border-gray-200 hover:border-gray-300'}`}>
          <input type="radio" name="type" value="url" checked={submitType==='url'} onChange={()=>setSubmitType('url')} className="sr-only"/>
          <div className="text-2xl mb-1">🔗</div>
          <div className="font-medium">URL</div>
        </label>
        <label className={`flex-1 p-4 border-2 rounded-lg cursor-pointer text-center transition-all ${submitType==='file'?'border-[#1b649e] bg-blue-50':'border-gray-200 hover:border-gray-300'}`}>
          <input type="radio" name="type" value="file" checked={submitType==='file'} onChange={()=>setSubmitType('file')} className="sr-only"/>
          <div className="text-2xl mb-1">📄</div>
          <div className="font-medium">File</div>
        </label>
      </div>
      
      {submitType==='url'&&<div>
        <label className="block text-sm font-medium text-gray-700 mb-1">URL to results</label>
        <input type="url" aria-label="URL to results" value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://..." required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1b649e] focus:border-transparent outline-none"/>
      </div>}
      
      {submitType==='file'&&<div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Upload file</label>
        <input type="file" aria-label="Upload file" onChange={e=>setFile(e.target.files[0])} accept=".pdf,.png,.jpg,.jpeg,.gif,.doc,.docx,.xls,.xlsx,.csv" required className="w-full px-4 py-2 border border-gray-300 rounded-lg"/>
        <p className="text-xs text-gray-500 mt-1">PDF, images, Word, Excel accepted</p>
      </div>}
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
        <textarea aria-label="Notes (optional)" value={notes} onChange={e=>setNotes(e.target.value)} placeholder="e.g. Season, match number, venue..." rows={3} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1b649e] focus:border-transparent outline-none resize-none"/>
      </div>
      
      {status==='error'&&<p className="text-red-600 text-sm">Something went wrong. Please try again.</p>}
      
      <button type="submit" disabled={submitting} className="w-full py-3 bg-[#1b649e] text-white rounded-lg hover:bg-[#134d7a] font-medium disabled:opacity-50">
        {submitting?'Submitting...':'Submit'}
      </button>
    </form>
  </div>;
};

