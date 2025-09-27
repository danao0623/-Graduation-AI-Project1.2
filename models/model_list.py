from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table
from sqlalchemy.orm import relationship,synonym
from init_db import Base

user_project = Table(
    'user_project',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user_account.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True)
)

class Project(Base):
    __tablename__ = 'projects'
    id               = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name             = Column(String(255), nullable=False, index=True)
    description      = Column(Text)
    architecture     = Column(String(255))
    frontend_language= Column(String(255), nullable=False)
    frontend_platform= Column(String(255))
    frontend_library = Column(String(255))
    backend_language = Column(String(255), nullable=False)
    backend_platform = Column(String(255))
    backend_library  = Column(String(255))
    users = relationship('UserAccount', secondary=user_project, back_populates='projects')

    # PK alias
    project_id = synonym('id') #synonym 讓 id 可以用 project_id 來取代

    use_cases       = relationship(
        'UseCase', back_populates='project', lazy='selectin',
        cascade='all, delete-orphan'
    )
    actors        = relationship(
        'Actor', back_populates='project', lazy='selectin',
        cascade='all, delete-orphan'
    )

class UseCase(Base):
    __tablename__       = 'use_cases'
    id                   = Column(Integer, primary_key=True, autoincrement=True)
    name                 = Column(String(255), nullable=False)
    description          = Column(Text)
    normal_process       = Column(String(255))
    exception_process    = Column(String(255))
    pre_condition        = Column(String(255))
    post_condition       = Column(String(255))
    trigger_condition    = Column(String(255))

    project_id           = Column(Integer, ForeignKey('projects.id'), nullable=False)
    use_case_id          = synonym('id')

    project              = relationship('Project', back_populates='use_cases', lazy='selectin')
    actors               = relationship('UseCaseActor', back_populates='use_case', lazy='selectin')
    event_lists          = relationship('EventList', back_populates='use_case', lazy='selectin')
    robustness_diagrams  = relationship('RobustnessDiagram', back_populates='use_case', lazy='selectin')
    sequence_diagrams    = relationship('SequenceDiagram', back_populates='use_case', lazy='selectin')

class UseCaseActor(Base):
    __tablename__ = 'use_case_actors'
    use_case_id   = Column(Integer, ForeignKey('use_cases.id'), primary_key=True)
    actor_id      = Column(Integer, ForeignKey('actors.id'), primary_key=True)


    use_case      = relationship('UseCase', back_populates='actors', lazy='selectin')
    actor         = relationship('Actor', back_populates='use_case_actors', lazy='selectin')

class Actor(Base):
    __tablename__ = 'actors'
    id             = Column(Integer, primary_key=True, autoincrement=True)
    name           = Column(String(255), nullable=False)

    actor_id       = synonym('id')

    project_id     = Column(Integer, ForeignKey('projects.id',ondelete='CASCADE'), nullable=False, index=True)
    
    use_case_actors= relationship('UseCaseActor', back_populates='actor', lazy='selectin')
    project        = relationship('Project', back_populates='actors', lazy='selectin')

class EventList(Base):
    __tablename__ = 'event_lists'
    id             = Column(Integer, primary_key=True, autoincrement=True)
    type           = Column(String(255))
    use_case_id    = Column(Integer, ForeignKey('use_cases.id'))

    event_list_id  = synonym('id')
    events         = relationship('Event', back_populates='event_list', lazy='selectin')
    use_case       = relationship('UseCase', back_populates='event_lists', lazy='selectin')

class Event(Base):
    __tablename__ = 'events'
    id             = Column(Integer, primary_key=True, autoincrement=True)
    sequence_no     = Column(Integer, nullable=False)           #事件在清單上的順序，1正常對1正常, 2例外對1、2、3例外
    type           = Column(String(255), nullable=False)        #事件類型        
    description    = Column(String(255), nullable=False)   
    event_list_id  = Column(Integer, ForeignKey('event_lists.id'))

    event_id       = synonym('id')  # synonym 讓 id 可以用 event_id 來取代
    event_list     = relationship('EventList', back_populates='events', lazy='selectin')

class RobustnessDiagram(Base):
    __tablename__ = 'robustness_diagrams'
    id                   = Column(Integer, primary_key=True, autoincrement=True)
    description          = Column(Text)
    use_case_id          = Column(Integer, ForeignKey('use_cases.id'))

    robustness_diagram_id = synonym('id')
    use_case              = relationship('UseCase', back_populates='robustness_diagrams', lazy='selectin')
    robustness_objects    = relationship('RobustnessObject', back_populates='robustness_diagram', lazy='selectin')
    sequence_diagrams     = relationship('SequenceDiagram', back_populates='robustness_diagram', lazy='selectin')

class RobustnessObject(Base):
    __tablename__ = 'robustness_objects'
    id             = Column(Integer, primary_key=True, autoincrement=True)
    robustness_diagram_id = Column(Integer, ForeignKey('robustness_diagrams.id'))
    object_id      = Column(Integer, ForeignKey('objects.id'))

    robustness_object_id = synonym('id')
    robustness_diagram   = relationship('RobustnessDiagram', back_populates='robustness_objects', lazy='selectin')
    object               = relationship('Object', back_populates='robustness_objects', lazy='selectin')

class SequenceDiagram(Base):
    __tablename__ = 'sequence_diagrams'
    id                   = Column(Integer, primary_key=True, autoincrement=True)
    robustness_diagram_id= Column(Integer, ForeignKey('robustness_diagrams.id'))
    use_case_id          = Column(Integer, ForeignKey('use_cases.id'))

    sequence_diagram_id = synonym('id')
    robustness_diagram  = relationship('RobustnessDiagram', back_populates='sequence_diagrams', lazy='selectin')
    use_case            = relationship('UseCase', back_populates='sequence_diagrams', lazy='selectin')
    objects             = relationship('ObjectSequenceDiagram', back_populates='sequence_diagram', lazy='selectin')
    sequence_events     = relationship('SequenceEvent', back_populates='sequence_diagram', lazy='selectin')

class SequenceEvent(Base):
    __tablename__ = 'sequence_events'
    id                   = Column(Integer, primary_key=True, autoincrement=True)
    sequence_event_name = Column(String(255), nullable=False)  #事件名稱
    sequence_no         = Column(Integer, nullable=False)       #事件在序列圖上的
    event_type        = Column(String(255), nullable=False)  #事件類型
    parameters     = Column(Text(255), nullable=False)
    sequence_diagram_id  = Column(Integer, ForeignKey('sequence_diagrams.id'))

    sequence_event_id = synonym('id')
    sequence_diagram  = relationship('SequenceDiagram', back_populates='sequence_events', lazy='selectin')

class ObjectSequenceDiagram(Base):
    __tablename__ = 'object_sequence_diagrams'
    object_id           = Column(Integer, ForeignKey('objects.id'), primary_key=True)
    sequence_diagram_id = Column(Integer, ForeignKey('sequence_diagrams.id'), primary_key=True)
    parameters          = Column(Text(255), nullable=False)
    object              = relationship('Object', back_populates='sequence_diagrams', lazy='selectin')
    sequence_diagram    = relationship('SequenceDiagram', back_populates='objects', lazy='selectin')

class Object(Base):
    __tablename__ = 'objects'
    id             = Column(Integer, primary_key=True, autoincrement=True)
    name           = Column(String(255), nullable=False)
    type           = Column(String(255))

    object_id      = synonym('id')

    robustness_objects  = relationship('RobustnessObject', back_populates='object', lazy='selectin')
    sequence_diagrams   = relationship('ObjectSequenceDiagram', back_populates='object', lazy='selectin')
    attributes         = relationship('Attributes', back_populates='object', lazy='selectin')
    methods            = relationship('Method', back_populates='object', lazy='selectin')

class Attributes(Base):
    __tablename__ = 'attributes'       #屬性
    id             = Column(Integer, primary_key=True, autoincrement=True)
    name           = Column(String(255), nullable=False)
    datatype       = Column(Text(255), nullable=False)
    visibility     = Column(String(255), nullable=False)  # public, private, protected
    
    object_id      = Column(Integer, ForeignKey('objects.id'), nullable=False)
           
    attribute_id = synonym('id')  # synonym 讓 id 可以用 attribute_id 來取代
    object         = relationship('Object', back_populates='attributes', lazy='selectin')

class   Method(Base):
    __tablename__ = 'methods'         #方法
    id             = Column(Integer, primary_key=True, autoincrement=True)
    name           = Column(String(255), nullable=False)
    return_type    = Column(Text(255), nullable=False)
    visibility     = Column(String(255), nullable=False)  # public, private, protected
    parameters     = Column(Text(255), nullable=False)  # 方法參數，格式為 JSON 字串或其他結構化格式
    
    object_id      = Column(Integer, ForeignKey('objects.id'), nullable=False)

    method_id      = synonym('id')  # synonym 讓 id 可以用 method_id 來取代
    object         = relationship('Object', back_populates='methods', lazy='selectin')

class UserAccount(Base):
    __tablename__ = 'user_account'    

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account = Column(String, unique=True, index=True)
    password = Column(String)
    projects = relationship('Project', secondary= user_project, back_populates='users')




