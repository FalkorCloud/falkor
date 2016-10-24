package.path = package.path .. ";/usr/local/openresty/nginx/lualib/?.lua"

local cjson = require "cjson"
local split = (require "stringutils").split


function do_auth(workspace)
	res = ngx.location.capture('/proxy?workspace=' .. workspace, {method = ngx.HTTP_GET, ctx = {headers = ngx.req.headers}})

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

	ngx.var.target = "v1.21/containers/" .. projects[workspace]["Id"] .. "/attach/ws?logs=1&stderr=1&stdout=1&stream=1&stdin=1"
end

local path = ngx.var.host
path = split(path, ".workspaces.")[1]


return do_auth(path)