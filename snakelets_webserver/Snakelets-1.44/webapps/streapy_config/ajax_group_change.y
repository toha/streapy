<%@session=yes%>

<form action="?action=change_group_change"method="post" name="form1"  >
<div class="form_reihe">
	<span class="form_label">Gruppenname:</span>
	<span class="form_input"><input class="input_feld" name="groupname" type="text" value="<%=getattr(self.RequestCtx, "groupname", "")%>" /></span>
</div>


<div class="form_reihe">
	<span class="form_label"></span>
	<span class="form_input"><input type="hidden" name="senden" value="true"  /><input type="hidden" name="groupid" value="<%=getattr(self.RequestCtx, "groupid", "")%>"  /><input class="input_button" type="submit" name="form_button" value="Abschicken"  /> </span>
</div>

</div>
<div class="clearer"></div>
</form>

