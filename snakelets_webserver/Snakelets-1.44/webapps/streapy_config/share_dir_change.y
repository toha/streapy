<%@pagetemplate="config_template.y"%>
<%@pagetemplatearg=title=Verzeichnis-Freigabe ändern%>
<%@session=yes%>


<div class="hidden ajax_load" id="ajax_loading"></div> 
<div class="cont_change hidden" id="reg_cont"></div>

<table>
	<tr>
		<th  class="width50">Freigabe</th><th>Aktion</th>
	</tr>

<%for u in self.RequestCtx.freigabe:
    folder_id = str(u[0])
    foldername = str(u[1])
    self.write('<tr><td class="width50"	>%s</td><td><a href="javascript:fadeInDirShareEdit(\'reg_cont\', %s);"><img src="pen.gif" width="12px" /></a> <a href="shareAdministration.sn?action=delete_dir_share&dir=%s"><img src="delete.gif" width="12px" /></a></td></tr>' %(foldername, folder_id, folder_id)) \%>

<%end%>

</table>

