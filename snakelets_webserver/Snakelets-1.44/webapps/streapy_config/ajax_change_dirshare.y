<%@session=yes%>

<form action=""method="post" name="form1"  >
<div class="form_reihe">
	<span class="form_label">Freigabe-Verzeichnis:</span>
	<span class="form_input"><input class="input_feld" name="freigabe" type="text" value="<%=getattr(self.RequestCtx, "freigabe", "")%>" /></span>
</div>



<div class="form_reihe">
	<span class="form_label">Benutzer-Filter:</span>
	<span class="form_input">
		<SELECT NAME="benutzer" class="input_feld" MULTIPLE SIZE=5>

		<%
        benutzer = []
        for ug in self.RequestCtx.user_has_share:
            benutzer += [int(ug[0])]
    
        for x in self.RequestCtx.user:          
            self.write('<OPTION VALUE="%s"' %(x[0])) 
            if int(x[0]) in  benutzer:
               self.write(' selected') 
  
			
            self.write('>%s' %(x[1])) \%>	
         <%end%>
		</SELECT>		
		
	</span>
</div>

<div class="form_reihe">
	<span class="form_label">Gruppen-Filter:</span>
	<span class="form_input">
		<SELECT NAME="gruppen" class="input_feld" MULTIPLE SIZE=5>

        <%
        gruppen = []
        for ug in self.RequestCtx.group_has_share:
            gruppen += [int(ug[0])]
    
        for x in self.RequestCtx.groups:          
            self.write('<OPTION VALUE="%s"' %(x[0])) 
            if int(x[0]) in  gruppen:
               self.write(' selected') 
  
            
            self.write('>%s' %(x[1])) \%>   
         <%end%>
		</SELECT>		
		
	</span>
</div>

<div class="form_reihe">
	<span class="form_label"></span>
	<span class="form_input"><input type="hidden" name="senden" value="true"  /><input type="hidden" name="folderid" value="<%=getattr(self.RequestCtx, "folderid", "")%>"  /><input class="input_button" type="submit" name="form_button" value="Abschicken"  /> </span>
</div>


<div class="clearer"></div>
</form>

