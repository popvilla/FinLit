const fs = require('fs');
const path = require('path');

describe('Repository cleanup', () => {
  test('docker-compose.yml does not contain placeholder secrets', () => {
    const compose = fs.readFileSync(path.join(__dirname, '..', 'docker-compose.yml'), 'utf8');
    expect(compose).not.toMatch(/your_mcp_secret_key_here/i);
    expect(compose).not.toMatch(/your_obsidian_plugin_api_key_here/i);
  });

  test('.env.example does not contain placeholder secrets', () => {
    const env = fs.readFileSync(path.join(__dirname, '..', '.env.example'), 'utf8');
    expect(env).not.toMatch(/your_mcp_secret_key_here/i);
    expect(env).not.toMatch(/your_obsidian_plugin_api_key_here/i);
  });

  test('frontend dependencies updated', () => {
    const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'frontend', 'package.json'), 'utf8'));
    expect(pkg.dependencies['@supabase/supabase-js']).toMatch(/^\^?2\.84\.0/);
    expect(pkg.dependencies.uuid).toMatch(/^\^?13\.0\.0/);
  });

  test('MCP dependencies updated', () => {
    const mcpPkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'Artemis Agentic Memory Layer(MCP)', 'package.json'), 'utf8'));
    expect(mcpPkg.dependencies.axios).toMatch(/^\^?1\.13\.2/);
    expect(mcpPkg.dependencies.express).toMatch(/^\^?5\.1\.0/);
    expect(mcpPkg.devDependencies.jest).toMatch(/^\^?30\.2\.0/);
  });
});
