<%@session=yes%>

<form action="?action=change_user_change"method="post" name="form1"  >
<div class="form_reihe">
	<span class="form_label">Benutzername:</span>
	<span class="form_input"><input class="input_feld" name="username" type="text" value="<%=getattr(self.RequestCtx, "username", "")%>" /></span>
</div>

<div class="form_reihe">
	<span class="form_label">Neues Passwort:</span>
	<span class="form_input"><input class="input_feld" name="pass1" type="password" /> </span>
</div>

<div class="form_reihe">
	<span class="form_label">Passwort zur Bestätigung:</span>
	<span class="form_input"><input class="input_feld" name="pass2" type="password" /> </span>
</div>
<div class="form_reihe">
	<span class="form_label">Mitglied in Gruppen:</span>
	<span class="form_input">
		<SELECT NAME="gruppen" class="input_feld" MULTIPLE SIZE=5>
		<%
         benutzergruppen = []
         print str(self.RequestCtx.usergroups)
         for ug in self.RequestCtx.usergroups:
             benutzergruppen += str(ug[0])

         for x in self.RequestCtx.groups:

             self.write('<OPTION VALUE="%s"' %(x[0])) 
             if str(x[0]) in benutzergruppen:
                 self.write(' SELECTED')		 
             self.write(' >%s</OPTION>' %(x[1]))  \%>	
		<%end%>
	
		</SELECT>
		
		
	</span>
</div>
<div class="form_reihe">
    <span class="form_label">Administrator:</span>
    <span class="form_input"><input type="checkbox" name="admin" value="1" <%=getattr(self.RequestCtx, "admin_check", "")%>>
</span>
</div>
<div class="form_reihe">
	<span class="form_label"></span>
	<span class="form_input"><input type="hidden" name="senden" value="true"  /><input type="hidden" name="userid" value="<%=getattr(self.RequestCtx, "userid", "")%>"  /><input class="input_button" type="submit" name="form_button" value="Abschicken"  /> </span>
</div>



</div>
<div class="clearer"></div>
</form>

