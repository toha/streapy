<%@pagetemplate="config_template.y"%>
<%@pagetemplatearg=title=Gruppenverwaltung - Gruppe hinzufügen%>
<%@session=yes%>

<%for x in self.RequestCtx.success_messages:
    self.write(x + "<br />") \%>

<%end%>

<%for x in self.RequestCtx.error_messages:
    self.write(x + "<br />") \%>

<%end%>

<form action=""method="post" name="form1"  >
<div class="form_reihe">
	<span class="form_label">Gruppenname:</span>
	<span class="form_input"><input class="input_feld" name="groupname" type="text" /></span>
</div>


<div class="form_reihe">
	<span class="form_label"></span>
	<span class="form_input"><input type="hidden" name="senden" value="true"  /><input class="input_button" type="submit" name="form_button" value="Abschicken"  /></span>
</div>

</div>
</form>
