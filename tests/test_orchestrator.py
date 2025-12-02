"""
Test suite for Ray Orchestrator
"""
import unittest
import asyncio
from uuid import uuid4

try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

from agent.src.orchestrator import get_orchestrator, RayOrchestrator, SingleThreadOrchestrator


class TestOrchestrator(unittest.TestCase):
    """Test both Ray and fallback orchestrators"""

    def test_get_orchestrator(self):
        """Test orchestrator factory"""
        orchestrator = get_orchestrator(max_concurrent_workers=3)

        if RAY_AVAILABLE:
            self.assertIsInstance(orchestrator, RayOrchestrator)
            self.assertEqual(orchestrator.max_workers, 3)
        else:
            self.assertIsInstance(orchestrator, SingleThreadOrchestrator)

    @unittest.skipUnless(RAY_AVAILABLE, "Ray not available")
    def test_ray_orchestrator_init(self):
        """Test Ray orchestrator initialization"""
        orchestrator = RayOrchestrator(max_concurrent_workers=2)
        self.assertFalse(orchestrator.initialized)

        orchestrator.initialize()
        self.assertTrue(orchestrator.initialized)
        self.assertTrue(ray.is_initialized())

        orchestrator.shutdown()
        self.assertFalse(orchestrator.initialized)

    def test_single_thread_orchestrator_init(self):
        """Test fallback orchestrator"""
        orchestrator = SingleThreadOrchestrator()
        self.assertIsNotNone(orchestrator.runner)


if __name__ == '__main__':
    unittest.main()
