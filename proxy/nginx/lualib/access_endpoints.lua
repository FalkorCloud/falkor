package.path = package.path .. ";/usr/local/openresty/nginx/lualib/?.lua"
local split = (require "stringutils").split


local path = ngx.var.host
path = split(path, ".endpoints.")[1]

--ngx.log(ngx.ERR, "PATH: " .. path) 

local vars = split(path, "-")

--tcp-172_19_0_4-8000
local protocol = vars[1]
local ip = vars[2]:gsub("_", ".")
local port = vars[3]


if port == "80" then
	ngx.say("401 Unauthorized: don't use endpoints to access the workspace.")
	return ngx.exit(401)
end

ngx.var.target = ip .. ":" .. port