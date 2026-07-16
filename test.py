import sys
import pytest
from Balancer import balancer
# add tests 

# simple server addition
def test_ring_add():
  nRing=balancer.ring()
  nRing.addServer(name="test_server",url="https://test_server")
  assert len(nRing.lookUp)==1,"server not added to the ring"
  assert "test_server" in nRing.lookUp,"server added with wrong name"
  assert len(nRing.lookUp["test_server"]) == balancer.VIRTUAL_PER_CONTAINER,"virtual servers not added appropriately"
# collision resolution
def test_collision_resolve():
  nRing=balancer.ring()
  nRing.slots[25]={"name":"bogus_object1"}
  nRing.slots[26]={"name":"bogus_object2"}
  nRing.slots[27]={"name":"bogus_object3"}
  nRing.addServer(name="test_server",url="https://test_server")
  assert nRing.slots[25]=={"name":"bogus_object1"}," bogus object overwritten hence collision resolution failed"
  assert nRing.slots[28]["name"]=="test_server"
# request allocation
def test_allocate_request():
  nRing=balancer.ring()
  nRing.slots[510]={"name":"bogus_object1"}
  nRing.slots[1]={"name":"bogus_object2"}
  val=nRing.allocateRequest(166)
  assert val,"request not allocated"
  assert val["name"]=="bogus_object2","request not allocated to correct server"

# same name addition
def test_same_name_add():
  nRing=balancer.ring()
  nRing.addServer(name="test_server",url="https://test_server")
  val=nRing.addServer(name="test_server",url="https://test_server")
  assert val==False,"same name addition not blocked"

# full ring addition prevention
def test_full_ring_add():
  nRing=balancer.ring()
  for i in range(0,int(balancer.SLOT_NO/balancer.VIRTUAL_PER_CONTAINER)):
    nRing.addServer(name=f"test_server_{i}",url=f"https://test_server_{i}")
  val=nRing.addServer(name="test_server",url="https://test_server")
  assert val==False
# confirm lookup attribution
def test_lookup():
  nRing=balancer.ring()
  nRing.addServer(name="test_server_1",url="https://test_server_1")
  nRing.addServer(name="test_server_2",url="https://test_server_2")
  assert len(nRing.lookUp)==2
  assert nRing.lookUp["test_server_1"],"failure to add first server"
  assert len(nRing.lookUp["test_server_1"])==balancer.VIRTUAL_PER_CONTAINER,"virtual servers not added correctly fer server 1"
  assert nRing.lookUp["test_server_2"],"failure to add second server"
  assert len(nRing.lookUp["test_server_2"])==balancer.VIRTUAL_PER_CONTAINER,"virtual servers not added correctly fer server 2"
# remove tests 
def test_ring_remove():
  nRing=balancer.ring()
  nRing.addServer(name="test_server",url="https://test_server")
  nRing.removeServer("test_server")
  assert len(nRing.lookUp)==0,"server not removed from ring"
  with pytest.raises(KeyError):
    nRing.lookUp["test_server"]


  





