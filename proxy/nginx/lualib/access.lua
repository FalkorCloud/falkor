package.path = package.path .. ";/usr/local/openresty/nginx/lualib/?.lua"

local cjson = require "cjson"
local split = (require "stringutils").split

function build_challenge(key, workspace, ip, timestamp)
	return ngx.encode_base64(ngx.hmac_sha1(key, workspace .. ":" .. ip .. ":" .. timestamp))
end


function do_auth(key, workspace)
	res = ngx.location.capture('/proxy?workspace=' .. workspace, {method = ngx.HTTP_GET, ctx = {headers = ngx.req.headers}})
	--ngx.log(ngx.ERR, res.body) 
	--ngx.log(ngx.ERR, res.status) 
	
	if res.status ~= 200 then
		ngx.say("401 Unauthorized: please login.")
		return ngx.exit(401)
	end
	
	local projects = cjson.new().decode(res.body)

	if not projects[workspace] then
		ngx.say("404 No such workspace")
		return ngx.exit(404)
	end
	
	if projects[workspace]["status"] ~= "running" then
		ngx.say("403 Forbidden: workspace not running.")
		return ngx.exit(403)
	end
   	
	local computed_hmac = build_challenge(key, workspace, projects[workspace]["IPAddress"], ngx.time())
	
	local cookie_value = computed_hmac .. ":" .. projects[workspace]["IPAddress"] .. ":" .. ngx.time()
	ngx.header["Set-Cookie"] = workspace .. "=" .. cookie_value .. "; Path=/; Expires=" .. ngx.cookie_time(ngx.time() + 60)
	
	ngx.var.target = projects[workspace]["IPAddress"] .. ":80"
end

--ngx.log(ngx.ERR, "URI: " .. ngx.var.host) 

local path = ngx.var.host
path = split(path, ".workspaces.")[1]

--ngx.log(ngx.ERR, "PATH: " .. path) 

local key = os.getenv('SECRET')
local cookie = ngx.var["cookie_" .. path]


if cookie ~= nil and cookie:find(":") ~= nil then
	local split_cookie = split(cookie, ":")
    local hmac = split_cookie[1]
    local ip = split_cookie[2]
    local timestamp = split_cookie[3]
    
    local computed_hmac = build_challenge(key, path, ip, timestamp)

    if computed_hmac == hmac and tonumber(timestamp) >= (ngx.time() - 60) then
    	ngx.var.target = ip .. ":80"
    	--if ngx.var.uri:find("ide.html") ~= nil then
    	  --ngx.req.set_uri_args({w="blooper"})
    	--end
    else
    	return do_auth(key, path)
    end
else
	return do_auth(key, path)
end


--ngx.log(ngx.ERR, "Connecting to workspace: " .. ngx.var.target) 