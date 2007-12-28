<%@pagetemplate="config_template.y"%>
<%@pagetemplatearg=title=Gruppenverwaltung%>
<%@session=yes%>


<div class="hidden ajax_load" id="ajax_loading"></div> 
<div class="cont_change hidden" id="reg_cont"></div>

<table>
	<tr>
		<th  class="width50">Gruppenname</th><th>Aktion</th>
	</tr>

<%for u in self.RequestCtx.group:
    groupid = str(u[0])
    groupname = str(u[1])
    self.write('<tr><td class="width50"	>%s</td><td><a href="javascript:fadeInGroupEdit(\'reg_cont\', %s);"><img src="pen.gif" width="12px" /></a> <a href="groupAdministration.sn?action=delete&groupid=%s"><img src="delete.gif" width="12px" /></a></td></tr>' %(groupname, groupid, groupid)) \%>

<%end%>

</table>

