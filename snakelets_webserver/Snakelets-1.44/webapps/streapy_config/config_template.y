<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="de" lang="de">
  <head>
    <title>streaPy configuration system -  <%=self.PageArgs.get('title','')%></title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link rel="stylesheet" type="text/css" href="stylesheet.css">
	<script type="text/javascript" src="ajax.js"></script>
	
	<script type="text/javascript">
		function setMenuColor(el) {	
			document.getElementById(el).style.backgroundColor = '#399ae8';
			document.getElementById(el).style.color = "#fff;"
		}
		function resetMenuColor(el) {
			document.getElementById(el).style.backgroundColor = '#fff';	
			document.getElementById(el).style.color = "#000;"
		}
		
var fade_round = 0;
var intervall = 100;
var max_rounds = 30;
var max_opacity = 100;
var aktiv = null;	
var akt_element = null

function fadeInDo(n, intervall) {
	fade_round += 1;
	if (aktiv != null) {
		if (fade_round >= max_rounds) {
			window.clearInterval(aktiv);
		}
	}
	act_opacity = max_opacity * (fade_round  / max_rounds);


	document.getElementById(akt_element).style.display = 'block';
    document.getElementById(akt_element).style.filter="Alpha(opacity=" +act_opacity+", finishopacity=0, style=2)";
    document.getElementById(akt_element).style.opacity = act_opacity / 100;     	
}

function fadeIn(el)
{	
	akt_element = el;
	fade_round = 0;
	document.getElementById(akt_element).style.display = 'none';
	document.getElementById("ajax_loading").style.display = 'block';
	document.getElementById("ajax_loading").innerHTML = '<img src="loading.gif" />'; 
	aktiv = window.setInterval("fadeInDo()", 50);	
}

function fadeInUserEdit(el, userid) {

	macheRequest('userAdministration.sn?action=ajax_change_user&userid=' + userid, getUserData);   
	fadeIn(el, userid);
}

function fadeInGroupEdit(el, groupid) {

	macheRequest('groupAdministration.sn?action=ajax_change_group&groupid=' + groupid, getUserData);   
	fadeIn(el);
}

function fadeInDirShareEdit(el, folderid) {

	macheRequest('shareAdministration.sn?action=ajax_change_dirshare&folderid=' + folderid, getUserData);   
	fadeIn(el);
}


function fadeInFileShareEdit(el, folderid) {

    macheRequest('shareFileAdministration.sn?action=ajax_change_fileshare&folderid=' + folderid, getUserData);   
    fadeIn(el);
}

function getUserData() 
{
        if (http_request.readyState == 4) {
            if (http_request.status == 200) {
				document.getElementById("ajax_loading").style.display = 'none';
				document.getElementById('reg_cont').innerHTML = http_request.responseText;
                
            } else {
                
            }
        } 
}  


	</script>
  <head>
  <body>
  

	<div class="header">
		<div class="logo">StreaPy <span class="subtitle">Configuration System</span></div>
	</div>
	<div class="subheader"></div>
	<div class="content">
		<h1><%=self.PageArgs.get('title','')%></h1>
		<%$insertpagebody%>
		
	</div>
	<div class="menu">
		<div class="menu_element_first" id="menu01" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);"><img src="menu_bullet.gif" /> <a href="serverConfig.sn?akt=change_server_details">Server-Einstellungen</a></div>
		<div class="menu_element" id="menu13" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" ><img src="menu_bullet.gif" /> Benutzerverwaltung</div>
		<div class="menu_element" id="menu02" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" /> <a href="userAdministration.sn?action=add">Benutzer hinzufügen</a></div>
		<div class="menu_element" id="menu03" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" /> <a href="userAdministration.sn?action=change">Benutzer bearbeiten</a></div>
		<div class="menu_element" id="menu04" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" ><img src="menu_bullet.gif" /> Gruppenverwaltung</div>
		<div class="menu_element" id="menu05" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" />  <a href="groupAdministration.sn?action=add">Gruppe hinzufügen</a></div>
		<div class="menu_element" id="menu06" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" />  <a href="groupAdministration.sn?action=change">Gruppe bearbeiten</a></div>
		<div class="menu_element" id="menu07" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" ><img src="menu_bullet.gif" /> Verzeichnis-Freigaben</div>
		<div class="menu_element" id="menu08" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" />  <a href="shareAdministration.sn?action=addDirShare">Verzeichnis freigeben</a></div>
		<div class="menu_element" id="menu09" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" />  <a href="shareAdministration.sn?action=changeDirShare">Freigaben bearbeiten</a></div>
		<div class="menu_element" id="menu10" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" ><img src="menu_bullet.gif" /> Datei-Rechte</div>
		<div class="menu_element" id="menu12" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" /> <a href="shareFileAdministration.sn?action=changeFileShare">Rechte bearbeiten</a></div>		
		<div class="menu_element" id="menu15" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" ><img src="menu_bullet.gif" /> Server-Optionen</div>
		<div class="menu_element" id="menu16" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" /> <a href="serverConfig.sn?akt=restart_server">Server neustarten</a></div>
		<div class="menu_element" id="menu17" onmouseover="setMenuColor(this.id);" onmouseout="resetMenuColor(this.id);" >&nbsp;&nbsp;&nbsp;&nbsp;<img src="menu_bullet.gif" /> <a href="serverConfig.sn?akt=reload_shares">Freigaben erneuern</a></div>		
	</div>
  
  </body>
</html>
