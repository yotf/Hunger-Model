def izdvoji_agente(model):
    return [a for a in model.schedule.agents if isinstance(a,HungryAgent)]

def compute_knowledge(model):
    """Ukupno znanje svih HungryAgenata"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in  agents:
        for key,value in agent.svet.items():
            assert(len(value)<=4)
            ukupno+=len(value)
    return ukupno

def total_pojedeni_otrovi(model):
    """Vraca broj ukupnih pojedenih otrova"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=agent.pojedeni_otrovi
    return ukupno

def total_pojedena_hrana(model):
    """Vraca broj ukupnih pojedenih otrova"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=agent.pojedena_hrana
    return ukupno

def measure_experience(model):
    """Ukupno iskustvo"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=len(agent.procedural)
    return ukupno

def total_energy(model):
    """Meri energiju svih agenata"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=agent.energy
        
    return ukupno
