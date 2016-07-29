local cjson = require "cjson"

function split(str, pat)
   local t = {}  -- NOTE: use {n = 0} in Lua-5.0
   local fpat = "(.-)" .. pat
   local last_end = 1
   local s, e, cap = str:find(fpat, 1)
   while s do
      if s ~= 1 or cap ~= "" then
	 table.insert(t,cap)
      end
      last_end = e+1
      s, e, cap = str:find(fpat, last_end)
   end
   if last_end <= #str then
      cap = str:sub(last_end)
      table.insert(t, cap)
   end
   return t
end

--ngx.log(ngx.ERR, "URI: " .. ngx.var.host) 

local path = ngx.var.host
path = split(path, ".workspaces.")[1]

--ngx.log(ngx.ERR, "PATH: " .. path) 


res = ngx.location.capture('/proxy?workspace=' .. path, {method = ngx.HTTP_GET, ctx = {headers = ngx.req.headers}})
--ngx.log(ngx.ERR, res.body) 
--ngx.log(ngx.ERR, res.status) 

if res.status ~= 200 then
	ngx.say("401 Unauthorized: please login.")
	return ngx.exit(401)
end

local projects = cjson.new().decode(res.body)

if not projects[path] then
	ngx.say("404 No such workspace")
	return ngx.exit(404)
end

if projects[path]["status"] ~= "running" then
	ngx.say("403 Forbidden: workspace not running.")
	return ngx.exit(403)
end


ngx.var.target = projects[path]["IPAddress"] .. ":80"

--ngx.log(ngx.ERR, "Connecting to workspace: " .. ngx.var.target) 