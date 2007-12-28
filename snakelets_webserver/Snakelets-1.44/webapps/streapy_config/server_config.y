<%@pagetemplate="config_template.y"%>
<%@pagetemplatearg=title=Server-Konfiguration%>
<%@session=yes%>


<%for x in self.RequestCtx.success_messages:
    self.write(x + "<br />") \%>

<%end%>

<%for x in self.RequestCtx.error_messages:
    self.write(x + "<br />") \%>

<%end%>



<form action="serverConfig.sn?akt=change_server_details&action=update"method="post" name="form1"  >
<div class="form_reihe">
	<span class="form_label">Server-IP:</span>
	<span class="form_input"><input class="input_feld" name="server_ip" type="text" value="<%=getattr(self.RequestCtx, "server_ip", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label">Server-Port:</span>
	<span class="form_input"><input class="input_feld" name="server_port" type="text" value="<%=getattr(self.RequestCtx, "server_port", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label">Max. Verbindungen:</span>
	<span class="form_input"><input class="input_feld" name="max_connections" type="text" value="<%=getattr(self.RequestCtx, "max_connections", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label">Max. Bandbreite / Benutzer:</span>
	<span class="form_input"><input class="input_feld" name="max_bandwith" type="text" value="<%=getattr(self.RequestCtx, "max_bandwith", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label">Docroot:</span>
	<span class="form_input"><input class="input_feld" name="server_docroot" type="text" value="<%=getattr(self.RequestCtx, "server_docroot", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label"></span>
	<span class="form_input"><input type="hidden" name="senden" value="true"  /><input class="input_button" type="submit" name="form_button" value="Abschicken"  /></span>
</div>

</div>
</form>


