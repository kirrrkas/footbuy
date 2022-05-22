from app import create_app, db
from app.models import Ticket, Role, Fan, FanID, Stadium, Match


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Fan=Fan, FanID=FanID, Role=Role,
                Ticket=Ticket, Stadium=Stadium, Match=Match)


if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run()
