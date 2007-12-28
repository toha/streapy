<%@pagetemplate="config_template.y"%>
<%@pagetemplatearg=title=Mitteilung%>
<%@session=yes%>

<%=getattr(self.RequestCtx, "message", "")%>