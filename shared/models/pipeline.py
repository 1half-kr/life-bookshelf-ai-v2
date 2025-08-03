"""
Pipeline base classes and interfaces
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

T = TypeVar('T')
R = TypeVar('R')


class StepStatus(Enum):
    """Pipeline step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepContext:
    """Context passed between pipeline steps"""
    pipeline_id: str
    step_name: str
    input_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the context"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the context"""
        return self.metadata.get(key, default)


@dataclass
class StepResult:
    """Result of a pipeline step execution"""
    step_name: str
    status: StepStatus
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_successful(self) -> bool:
        """Check if step execution was successful"""
        return self.status == StepStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if step execution failed"""
        return self.status == StepStatus.FAILED


@dataclass
class PipelineResult:
    """Result of entire pipeline execution"""
    pipeline_id: str
    pipeline_name: str
    status: StepStatus
    step_results: List[StepResult] = field(default_factory=list)
    total_execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def add_step_result(self, result: StepResult) -> None:
        """Add a step result to the pipeline result"""
        self.step_results.append(result)
        self.total_execution_time += result.execution_time
    
    @property
    def is_successful(self) -> bool:
        """Check if entire pipeline execution was successful"""
        return (self.status == StepStatus.COMPLETED and 
                all(step.is_successful for step in self.step_results))
    
    @property
    def failed_steps(self) -> List[StepResult]:
        """Get list of failed steps"""
        return [step for step in self.step_results if step.is_failed]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of steps"""
        if not self.step_results:
            return 0.0
        successful_steps = sum(1 for step in self.step_results if step.is_successful)
        return successful_steps / len(self.step_results)


class PipelineStep(ABC, Generic[T, R]):
    """Abstract base class for pipeline steps"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, context: StepContext) -> StepResult:
        """Execute the pipeline step"""
        pass
    
    async def validate_input(self, context: StepContext) -> bool:
        """Validate input data for the step"""
        return True
    
    async def cleanup(self, context: StepContext) -> None:
        """Cleanup resources after step execution"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


class Pipeline(ABC):
    """Abstract base class for pipelines"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.steps: List[PipelineStep] = []
        self.pipeline_id = str(uuid.uuid4())
    
    def add_step(self, step: PipelineStep) -> None:
        """Add a step to the pipeline"""
        self.steps.append(step)
    
    async def execute(self, input_data: Dict[str, Any]) -> PipelineResult:
        """Execute the entire pipeline"""
        result = PipelineResult(
            pipeline_id=self.pipeline_id,
            pipeline_name=self.name,
            status=StepStatus.RUNNING
        )
        
        start_time = datetime.utcnow()
        
        try:
            context = StepContext(
                pipeline_id=self.pipeline_id,
                step_name="",
                input_data=input_data
            )
            
            # Execute steps sequentially
            for step in self.steps:
                context.step_name = step.name
                step_result = await self._execute_step(step, context)
                result.add_step_result(step_result)
                
                # Stop pipeline if step failed and no error handling
                if step_result.is_failed and not self._should_continue_on_error(step):
                    result.status = StepStatus.FAILED
                    break
                
                # Update context with step output
                context.input_data.update(step_result.output_data)
            
            # Set final status
            if result.status != StepStatus.FAILED:
                result.status = StepStatus.COMPLETED
            
        except Exception as e:
            result.status = StepStatus.FAILED
            # Add error step result
            error_result = StepResult(
                step_name="pipeline_error",
                status=StepStatus.FAILED,
                error_message=str(e)
            )
            result.add_step_result(error_result)
        
        finally:
            result.completed_at = datetime.utcnow()
            result.total_execution_time = (
                result.completed_at - start_time
            ).total_seconds()
        
        return result
    
    async def _execute_step(
        self, 
        step: PipelineStep, 
        context: StepContext
    ) -> StepResult:
        """Execute a single step with error handling"""
        step_start_time = datetime.utcnow()
        
        try:
            # Validate input
            if not await step.validate_input(context):
                return StepResult(
                    step_name=step.name,
                    status=StepStatus.FAILED,
                    error_message="Input validation failed"
                )
            
            # Execute step
            result = await step.execute(context)
            result.execution_time = (
                datetime.utcnow() - step_start_time
            ).total_seconds()
            
            return result
            
        except Exception as e:
            return StepResult(
                step_name=step.name,
                status=StepStatus.FAILED,
                error_message=str(e),
                execution_time=(
                    datetime.utcnow() - step_start_time
                ).total_seconds()
            )
        
        finally:
            # Cleanup step resources
            try:
                await step.cleanup(context)
            except Exception:
                pass  # Ignore cleanup errors
    
    def _should_continue_on_error(self, step: PipelineStep) -> bool:
        """Check if pipeline should continue after step error"""
        return step.get_config("continue_on_error", False)
    
    @abstractmethod
    def build_pipeline(self) -> None:
        """Build the pipeline by adding steps"""
        pass
