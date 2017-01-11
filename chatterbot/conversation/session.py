import uuid


class StatementManager(object):
    """
    Provides methods for adding and retrieving statements
    for this conversation in the database.
    """

    def __init__(self, storage, conversation_id):
        self.storage = storage
        self.conversation_id = conversation_id

    def all(self):
        """
        Return all statements in the conversation.
        """
        return self.storage.filter(
            conversation__id=self.conversation_id,
            order_by='created_at'
        )

    def add(self, statement):
        """
        Add a statement to the conversation.
        """
        self.storage.update(statement)

    def count(self):
        return len(self.all())

    def exists(self):
        return self.count() > 0


class Session(object):
    """
    A single chat session.
    In the future this class will be renamed to `Conversation`.
    """

    def __init__(self, storage):
        super(Session, self).__init__()

        self.storage = storage

        # A unique identifier for the chat session
        self.uuid = uuid.uuid1()
        self.id_string = str(self.uuid)
        self.id = str(self.uuid)

        # The last 10 statement inputs and outputs
        self.statements = StatementManager(self.storage, self.id)

    def get_last_response_statement(self):
        """
        Return the last statement that was received.
        """
        statements = self.statements.all()
        if statements:
            return statements[1]
        return None


class ConversationSessionManager(object):
    """
    Object to hold and manage multiple chat sessions.
    """

    def __init__(self, storage):
        self.storage = storage
        self.sessions = {}

    def new(self):
        """
        Add a new chat session.
        """
        session = self.storage.create_conversation()

        self.sessions[session.id_string] = session

        return session

    def get(self, session_id, default=None):
        """
        Return a session given a unique identifier.
        """
        return self.sessions.get(str(session_id), default)

    def update(self, session_id, conversance):
        """
        Add a conversance to a given session if the session exists.
        """
        session_id = str(session_id)
        if session_id in self.sessions:
            for statement in conversance:
                self.sessions[session_id].statements.add(statement)

