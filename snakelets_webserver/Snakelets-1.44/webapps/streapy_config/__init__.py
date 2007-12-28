# configuration for this webapp
import server_config, user_administration, group_administration, share_administration, share_file_administration, user_auth

name="streaPy configuration Application"

docroot="."

snakelets={
	"serverConfig.sn": server_config.ServerConfig,
	"userAdministration.sn": user_administration.UserAdministration,
	"groupAdministration.sn": group_administration.GroupAdministration,
	"shareAdministration.sn": share_administration.ShareAdministration,
	"shareFileAdministration.sn": share_file_administration.ShareFileAdministration,
	"userAuth.sn": user_auth.userAuth
}

def dirListAllower(path):
	# path will be RELATIVE for this webapp, and NOT starting with /

	# this (root)webapp allows ALL dirs to be viewed
	return True
