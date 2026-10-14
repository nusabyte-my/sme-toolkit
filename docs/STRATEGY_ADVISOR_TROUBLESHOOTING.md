# Strategy Advisor System Troubleshooting Guide

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Backend Issues](#backend-issues)
3. [Frontend Issues](#frontend-issues)
4. [API Issues](#api-issues)
5. [Database Issues](#database-issues)
6. [Performance Issues](#performance-issues)
7. [Agent Issues](#agent-issues)
8. [Security Issues](#security-issues)

## Installation Issues

### Backend Won't Start

**Symptoms:**
- `uvicorn` command fails
- Module import errors
- Port already in use

**Solutions:**

1. **Check Python Version**
   ```bash
   python --version
   # Should be 3.9+
   ```

2. **Install Dependencies**
   ```bash
   cd sme-toolkit-backend
   pip install -r requirements.txt
   # Or with poetry:
   poetry install
   ```

3. **Check Port Availability**
   ```bash
   # Linux/macOS
   netstat -an | grep 8000
   # Windows
   netstat -an | findstr :8000
   ```

4. **Kill Existing Process**
   ```bash
   # Find and kill process
   lsof -ti:8000 | xargs kill -9
   ```

5. **Check Environment Variables**
   ```bash
   # Verify .env file exists
   ls -la .env
   
   # Check required variables
   grep DATABASE_URL .env
   grep GEMINI_API_KEY .env
   ```

### Frontend Won't Start

**Symptoms:**
- `npm run dev` fails
- Module not found errors
- Port already in use

**Solutions:**

1. **Check Node Version**
   ```bash
   node --version
   # Should be 18+
   ```

2. **Clear Cache and Reinstall**
   ```bash
   rm -rf node_modules
   rm package-lock.json
   npm install
   ```

3. **Check Port Availability**
   ```bash
   # Linux/macOS
   lsof -ti:5173 | xargs kill -9
   # Windows
   netstat -an | findstr :5173
   ```

4. **Check Environment Variables**
   ```bash
   # Verify .env.local exists
   ls -la .env.local
   
   # Check required variables
   grep VITE_API_BASE_URL .env.local
   ```

5. **TypeScript Errors**
   ```bash
   # Check for type errors
   npm run type-check
   
   # Fix type errors
   npm run build
   ```

## Backend Issues

### Database Connection Errors

**Symptoms:**
- `OperationalError: unable to open database file`
- `ConnectionRefusedError: can't connect to database`
- Slow database queries

**Solutions:**

1. **Check Database URL**
   ```bash
   # Verify DATABASE_URL in .env
   cat .env | grep DATABASE_URL
   ```

2. **Check Database Server**
   ```bash
   # For PostgreSQL
   pg_isready -h localhost -p 5432
   
   # For SQLite
   ls -la sme_toolkit.db
   ```

3. **Check Permissions**
   ```bash
   # Check file permissions
   ls -la sme_toolkit.db
   
   # Fix permissions
   chmod 644 sme_toolkit.db
   ```

4. **Optimize Queries**
   ```python
   # Add indexes
   CREATE INDEX idx_profile_id ON company_goals(business_profile_id);
   
   # Use select specific columns
   session.query(CompanyGoal.id, CompanyGoal.title).filter(...)
   ```

### API Service Errors

**Symptoms:**
- `503 Service Unavailable`
- `504 Gateway Timeout`
- Slow API responses

**Solutions:**

1. **Check AI Service**
   ```bash
   # Verify Gemini API key
   curl -H "Authorization: Bearer YOUR_KEY" \
     https://generativelanguage.googleapis.com/v1/models
   
   # Check API quota
   # Visit: https://console.cloud.google.com/ai
   ```

2. **Increase Timeout**
   ```python
   # In service configuration
   timeout = 60  # Increase from default 30
   ```

3. **Check Network Connectivity**
   ```bash
   # Test connection
   ping google.com
   
   # Check DNS
   nslookup google.com
   ```

4. **Enable Caching**
   ```python
   # Cache frequently accessed data
   from app.services.cache_service import get_cache
   cache = get_cache()
   cache.set("key", value, ttl=300)
   ```

### Agent Execution Failures

**Symptoms:**
- Agents returning errors
- Timeout during agent execution
- Incomplete agent results

**Solutions:**

1. **Check Agent Configuration**
   ```python
   # Verify agent is properly initialized
   from app.agents.goal_advisor_agent import GoalAdvisorAgent
   agent = GoalAdvisorAgent()
   ```

2. **Increase Timeout**
   ```python
   # Increase agent timeout
   result = await agent.invoke(data, timeout=60)
   ```

3. **Check AI Service Status**
   ```bash
   # Verify Gemini API is working
   curl https://generativelanguage.googleapis.com/v1/models
   ```

4. **Implement Retry Logic**
   ```python
   # Add retry with exponential backoff
   import asyncio
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   async def invoke_with_retry(data):
       return await agent.invoke(data)
   ```

## Frontend Issues

### Component Rendering Errors

**Symptoms:**
- Blank screens
- Components not rendering
- React errors in console

**Solutions:**

1. **Check Component Imports**
   ```typescript
   // Verify correct import path
   import ScoreGauge from '../components/strategy/ScoreGauge'
   ```

2. **Check Props**
   ```typescript
   // Verify required props are provided
   <ScoreGauge score={75} label="Business Health" />
   ```

3. **Check State**
   ```typescript
   // Verify state is initialized
   const [analysis, setAnalysis] = useState<Analysis | null>(null)
   ```

4. **Clear Browser Cache**
   ```bash
   # Clear cache and reload
   # Chrome: Ctrl+Shift+Delete
   # Firefox: Ctrl+Shift+Delete
   # Safari: Cmd+Option+E
   ```

### API Integration Errors

**Symptoms:**
- Network errors
- CORS errors
- Authentication errors

**Solutions:**

1. **Check API URL**
   ```typescript
   // Verify VITE_API_BASE_URL
   console.log(import.meta.env.VITE_API_BASE_URL)
   ```

2. **Check CORS Configuration**
   ```python
   # In backend main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
   )
   ```

3. **Check Authentication**
   ```typescript
   // Verify token is set
   const token = localStorage.getItem('auth_token')
   
   // Add token to requests
   headers: {
       'Authorization': `Bearer ${token}`
   }
   ```

4. **Handle Errors Gracefully**
   ```typescript
   // Add error boundaries
   try {
       const response = await api.call()
       return response.data
   } catch (error) {
       console.error('API Error:', error)
       setError(error.message)
   }
   ```

### Performance Issues

**Symptoms:**
- Slow page loads
- Laggy interactions
- High memory usage

**Solutions:**

1. **Implement Code Splitting**
   ```typescript
   // Lazy load components
   const OpportunityCard = lazy(() => import('./OpportunityCard'))
   ```

2. **Optimize Re-renders**
   ```typescript
   // Use React.memo
   export default React.memo(function OpportunityCard({ data }) {
       return <div>{data.title}</div>
   })
   ```

3. **Implement Virtual Scrolling**
   ```typescript
   // For large lists
   import { FixedSizeList as List } from 'react-window'
   
   <List
       height={600}
       itemCount={items.length}
       itemSize={35}
   >
       {({ index, style }) => (
           <div style={style}>{items[index].title}</div>
       )}
   </List>
   ```

4. **Debounce API Calls**
   ```typescript
   // Debounce search/input
   import { debounce } from 'lodash'
   
   const debouncedSearch = debounce((query: string) => {
       performSearch(query)
   }, 300)
   ```

## API Issues

### Rate Limiting

**Symptoms:**
- `429 Too Many Requests`
- Requests being blocked
- Slow responses

**Solutions:**

1. **Implement Exponential Backoff**
   ```typescript
   // Add retry with backoff
   const retryWithBackoff = async (fn: Function, retries: number = 3) => {
       for (let i = 0; i < retries; i++) {
           try {
               return await fn()
           } catch (error) {
               if (i === retries - 1) throw error
               await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000))
           }
       }
   }
   ```

2. **Implement Request Queuing**
   ```typescript
   // Queue requests
   class RequestQueue {
       private queue: Array<() => Promise<any>> = []
       private processing = false
       
       async add(request: () => Promise<any>) {
           this.queue.push(request)
           if (!this.processing) {
               this.processQueue()
           }
       }
       
       private async processQueue() {
           this.processing = true
           while (this.queue.length > 0) {
               const request = this.queue.shift()
               await request()
           }
           this.processing = false
       }
   }
   ```

3. **Cache Responses**
   ```typescript
   // Cache API responses
   const cache = new Map<string, any>()
   
   async function getCachedData(key: string) {
       if (cache.has(key)) {
           return cache.get(key)
       }
       const data = await fetchData(key)
       cache.set(key, data)
       return data
   }
   ```

### Authentication Errors

**Symptoms:**
- `401 Unauthorized`
- Token expired
- Invalid credentials

**Solutions:**

1. **Refresh Token**
   ```typescript
   // Implement token refresh
   async function refreshToken() {
       const refreshToken = localStorage.getItem('refresh_token')
       const response = await api.post('/auth/refresh', { refresh_token })
       localStorage.setItem('auth_token', response.data.access_token)
       return response.data.access_token
   }
   ```

2. **Handle Token Expiry**
   ```typescript
   // Check token expiry
   function isTokenExpired(token: string): boolean {
       const payload = JSON.parse(atob(token.split('.')[1]))
       return payload.exp < Date.now() / 1000
   }
   ```

3. **Clear Invalid Tokens**
   ```typescript
   // Clear invalid tokens
   function clearInvalidTokens() {
       localStorage.removeItem('auth_token')
       localStorage.removeItem('refresh_token')
       window.location.href = '/login'
   }
   ```

## Database Issues

### Slow Queries

**Symptoms:**
- Queries taking > 1 second
- Database timeouts
- High CPU usage

**Solutions:**

1. **Add Indexes**
   ```sql
   -- Create composite index
   CREATE INDEX idx_profile_type_date 
   ON score_records(business_profile_id, score_type, calculated_at);
   
   -- Create partial index
   CREATE INDEX idx_score_value 
   ON score_records(overall_score);
   ```

2. **Optimize Queries**
   ```python
   # Use select specific columns
   session.query(
       CompanyGoal.id,
       CompanyGoal.title,
       CompanyGoal.status
   ).filter(CompanyGoal.business_profile_id == profile_id)
   
   # Use joins efficiently
   session.query(CompanyGoal)\
       .join(BusinessProfile)\
       .filter(BusinessProfile.id == profile_id)
   ```

3. **Use Pagination**
   ```python
   # Paginate large result sets
   def get_goals_paginated(profile_id: str, page: int = 1, limit: int = 20):
       offset = (page - 1) * limit
       return session.query(CompanyGoal)\
           .filter(CompanyGoal.business_profile_id == profile_id)\
           .offset(offset)\
           .limit(limit)\
           .all()
   ```

### Connection Pool Exhaustion

**Symptoms:**
- `Connection pool exhausted`
- Unable to get database connection
- Connection timeouts

**Solutions:**

1. **Increase Pool Size**
   ```python
   # In database.py
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,  # Increase from default 5
       max_overflow=10
   )
   ```

2. **Implement Connection Recycling**
   ```python
   # Recycle connections
   engine = create_async_engine(
       DATABASE_URL,
       pool_recycle=3600,  # Recycle every hour
       pool_pre_ping=True
   )
   ```

3. **Use Connection Pooling**
   ```python
   # Use async session factory
   async_session_maker = async_sessionmaker(
       bind=engine,
       class_=AsyncSession,
       expire_on_commit=False
   )
   ```

## Performance Issues

### Slow API Responses

**Symptoms:**
- API responses > 2 seconds
- Timeouts
- Poor user experience

**Solutions:**

1. **Enable Response Compression**
   ```python
   # In main.py
   from fastapi.middleware.gzip import GZipMiddleware
   
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

2. **Optimize Database Queries**
   ```python
   # Use query optimization
   # See Database Issues section
   ```

3. **Implement Caching**
   ```python
   # Cache frequently accessed data
   from app.services.cache_service import get_cache
   
   cache = get_cache()
   cached_data = cache.get("key")
   if cached_data:
       return cached_data
   ```

4. **Use Async Operations**
   ```python
   # Use async/await for I/O operations
   async def get_data():
       data = await fetch_from_db()
       return data
   ```

### High Memory Usage

**Symptoms:**
- Out of memory errors
- Slow performance
- System crashes

**Solutions:**

1. **Monitor Memory Usage**
   ```python
   # Add memory monitoring
   import psutil
   
   def check_memory():
       process = psutil.Process()
       print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")
   ```

2. **Optimize Data Structures**
   ```python
   # Use generators instead of lists
   def get_large_dataset():
       for item in fetch_items():
           yield process_item(item)
   ```

3. **Clear Cache Periodically**
   ```python
   # Clear old cache entries
   cache.clear()
   ```

## Agent Issues

### Agent Not Responding

**Symptoms:**
- Agent timeout
- No response from agent
- Partial results

**Solutions:**

1. **Check Agent Configuration**
   ```python
   # Verify agent is initialized
   from app.agents.goal_advisor_agent import GoalAdvisorAgent
   agent = GoalAdvisorAgent()
   ```

2. **Increase Timeout**
   ```python
   # Increase agent timeout
   result = await agent.invoke(data, timeout=60)
   ```

3. **Check AI Service**
   ```bash
   # Verify Gemini API is working
   curl https://generativelanguage.googleapis.com/v1/models
   ```

4. **Implement Fallback**
   ```python
   # Add fallback logic
   try:
       result = await agent.invoke(data)
   except Exception as e:
       return get_fallback_result(data)
   ```

### Conflicting Agent Results

**Symptoms:**
- Agents giving conflicting advice
- Inconsistent scores
- Contradictory recommendations

**Solutions:**

1. **Implement Conflict Resolution**
   ```python
   # Use conflict resolver
   from app.utils.conflict_resolution import ConflictResolver
   
   resolver = ConflictResolver()
   resolved = resolver.resolve_score_conflicts(agent_results)
   ```

2. **Weight Agent Results**
   ```python
   # Weight by confidence
   def weighted_average(results: list, weights: list):
       total = sum(r * w for r, w in zip(results, weights))
       return total / sum(weights)
   ```

3. **Flag for Manual Review**
   ```python
   # Flag conflicts for review
   if has_conflicts(results):
       return {
           "results": results,
           "conflicts": detected_conflicts,
           "requires_review": True
       }
   ```

## Security Issues

### CORS Errors

**Symptoms:**
- CORS policy errors
- Requests blocked
- Mixed content errors

**Solutions:**

1. **Configure CORS Properly**
   ```python
   # In main.py
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:5173",
           "https://your-domain.com"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Use HTTPS in Production**
   ```python
   # Configure SSL/TLS
   uvicorn app.main:app \
       --host 0.0.0.0 \
       --port 8000 \
       --ssl-keyfile /path/to/key.pem \
       --ssl-certfile /path/to/cert.pem
   ```

3. **Validate Origins**
   ```python
   # Validate request origin
   @app.middleware("http")
   async def validate_origin(request: Request, call_next):
       origin = request.headers.get("origin")
       if origin not in ALLOWED_ORIGINS:
           raise HTTPException(status_code=403, detail="Origin not allowed")
       response = await call_next(request)
       response.headers["Access-Control-Allow-Origin"] = origin
       return response
   ```

### SQL Injection

**Symptoms:**
- Database errors
- Unexpected behavior
- Data corruption

**Solutions:**

1. **Use Parameterized Queries**
   ```python
   # Use SQLAlchemy ORM
   session.query(CompanyGoal).filter(
       CompanyGoal.id == goal_id
   ).first()
   
   # NOT:
   session.execute(f"SELECT * FROM goals WHERE id = '{goal_id}'")
   ```

2. **Validate Input**
   ```python
   # Validate and sanitize input
   from pydantic import validator
   
   @validator('title')
   def validate_title(cls, v):
       if not v or len(v) > 255:
           raise ValueError('Title must be 1-255 characters')
       return v
   ```

3. **Use ORM Methods**
   ```python
   # Use ORM methods instead of raw SQL
   goal = session.query(CompanyGoal).get(goal_id)
   ```

### XSS Vulnerabilities

**Symptoms:**
- Script injection
- Data theft
- Unauthorized actions

**Solutions:**

1. **Sanitize User Input**
   ```typescript
   // Sanitize input
   import DOMPurify from 'dompurify'
   
   const cleanInput = DOMPurify.sanitize(userInput)
   ```

2. **Use React's Built-in Protection**
   ```typescript
   // React automatically escapes JSX
   const userContent = '<script>alert("XSS")</script>'
   return <div>{userContent}</div>  // React escapes this
   ```

3. **Content Security Policy**
   ```html
   <!-- Add CSP header -->
   <meta http-equiv="Content-Security-Policy" 
         content="default-src 'self'; script-src 'self' 'unsafe-inline'">
   ```

## Getting Help

### Collect Diagnostic Information

When reporting issues, collect:

1. **System Information**
   ```bash
   # OS and version
   uname -a
   
   # Python version
   python --version
   
   # Node version
   node --version
   ```

2. **Application Logs**
   ```bash
   # Backend logs
   tail -f sme_toolkit.log
   
   # Frontend logs (browser console)
   # Check browser console for errors
   ```

3. **Error Messages**
   ```bash
   # Copy exact error messages
   # Include stack traces
   # Note steps to reproduce
   ```

4. **Configuration**
   ```bash
   # Environment variables
   cat .env
   
   # Configuration files
   cat config.json
   ```

### Contact Support

- **Email**: support@sme-toolkit.com
- **Documentation**: https://docs.sme-toolkit.com
- **Issues**: https://github.com/your-org/sme-toolkit/issues
- **Discord**: https://discord.gg/sme-toolkit

### Community Resources

- **GitHub Discussions**: https://github.com/your-org/sme-toolkit/discussions
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/sme-toolkit
- **Reddit**: https://reddit.com/r/sme-toolkit

## Common Error Codes

| Code | Description | Solution |
|-------|-------------|----------|
| 400 | Bad Request | Check request body and parameters |
| 401 | Unauthorized | Check authentication token |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify resource exists |
| 422 | Validation Error | Fix input validation errors |
| 429 | Too Many Requests | Implement rate limiting |
| 500 | Internal Server Error | Check server logs |
| 503 | Service Unavailable | Check service status |

## Best Practices

1. **Always check logs first**
2. **Reproduce the issue locally**
3. **Search existing issues before creating new ones**
4. **Provide detailed error messages and stack traces**
5. **Include steps to reproduce**
6. **Test fixes thoroughly before deploying**
7. **Keep dependencies updated**
8. **Monitor system performance regularly**
9. **Implement proper error handling**
10. **Use version control for all changes**
