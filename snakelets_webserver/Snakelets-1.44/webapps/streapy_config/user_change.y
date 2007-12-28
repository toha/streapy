<%@pagetemplate="config_template.y"%>
<%@pagetemplatearg=title=Benutzerverwaltung - Benutzer verwalten%>
<%@session=yes%>


<div class="hidden ajax_load" id="ajax_loading"></div> 
<div class="cont_change hidden" id="reg_cont"></div>

<table>
	<tr>
		<th  class="width50">Benutzername</th><th>Aktion</th>
	</tr>

<%for u in self.RequestCtx.user:
    userid = str(u[0])
    username = str(u[1])
    self.write('<tr><td class="width50"	>%s</td><td><a href="javascript:fadeInUserEdit(\'reg_cont\', %s);"><img src="pen.gif" width="12px" /></a> <a href="userAdministration.sn?action=delete&userid=%s"><img src="delete.gif" width="12px" /></a></td></tr>' %(username, userid, userid)) \%>

<%end%>

</table>

