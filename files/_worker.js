// Cloudflare Pages worker. Everything is served as normal static files,
// except /__ping which just proves this worker is running.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/__ping') return new Response('worker ok');
    return env.ASSETS.fetch(request);
  }
};
