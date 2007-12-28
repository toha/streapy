<%@pagetemplate="config_template.y"%>
<%@pagetemplatearg=title=Benutzerverwaltung - Benutzer hinzufügen%>


<%for x in self.RequestCtx.success_messages:
    self.write(x + "<br />") \%>

<%end%>

<%for x in self.RequestCtx.error_messages:
    self.write(x + "<br />") \%>

<%end%>

<form action=""method="post" name="form1"  >
<div class="form_reihe">
	<span class="form_label">Benutzername:</span>
	<span class="form_input"><input class="input_feld" name="username" type="text" value="<%=getattr(self.RequestCtx, "server_ip", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label">Passwort:</span>
	<span class="form_input"><input class="input_feld" name="pass1" type="password" value="<%=getattr(self.RequestCtx, "server_port", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label">Passwort zur Bestätigung:</span>
	<span class="form_input"><input class="input_feld" name="pass2" type="password" value="<%=getattr(self.RequestCtx, "max_connections", "")%>" /></span>
</div>
<div class="form_reihe">
	<span class="form_label">Mitglied in Gruppen:</span>
	<span class="form_input">
		<SELECT NAME="gruppen" class="input_feld" MULTIPLE SIZE=5>

		<%for x in self.RequestCtx.groups:
		    self.write('<OPTION VALUE="%s">%s' %(x[0], x[1])) \%>	
		<%end%>
		</SELECT>
		
		
	</span>
</div>


<div class="form_reihe">
	<span class="form_label"></span>
	<span class="form_input"><input type="hidden" name="senden" value="true"  /><input class="input_button" type="submit" name="form_button" value="Abschicken"  /></span>
</div>

</div>
</form>
